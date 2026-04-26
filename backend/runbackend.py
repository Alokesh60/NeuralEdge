# runbackend.py – CV Bias Scanner (Optimized)
import os, io, json, base64, numpy as np, cv2
from PIL import Image
from fastapi import FastAPI, File, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import torch, torch.nn as nn
from torchvision.models import resnet50
import torchvision.transforms as T
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image

app = FastAPI(title="CV Bias Scanner", version="2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = resnet50()
model.fc = nn.Linear(model.fc.in_features, 2)
model.load_state_dict(torch.load(os.path.join("..", "fairness_model.pt"), map_location=device))
model.to(device).eval()

with open(os.path.join("..", "fairness_results.json")) as f:
    fairness = json.load(f)

transform = T.Compose([
    T.Resize((224, 224)), T.ToTensor(),
    T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])



async def _process_image(file: UploadFile):
    """
    Read uploaded file once → keep raw bytes for Grad-CAM reuse.
    Returns: (PIL img, raw bytes, numpy float32 224×224, softmax probs, pred int)
    Inference runs inside torch.no_grad() so the main tensor never needs grads.
    """
    raw   = await file.read()
    img   = Image.open(io.BytesIO(raw)).convert("RGB")
    np_img = np.array(img.resize((224, 224))) / 255.0   
    t     = transform(img).unsqueeze(0).to(device)
    with torch.no_grad():
        probs = torch.softmax(model(t), dim=1)[0]
        pred  = int(probs.argmax().item())
    return img, raw, np_img, probs, pred


def _run_gradcam(raw_bytes: bytes, np_img: np.ndarray):

    try:
        img_fresh = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
        t_grad    = transform(img_fresh).unsqueeze(0).to(device)
       
        cam = GradCAM(model=model, target_layers=[model.layer4[-1]])
        hm  = cam(input_tensor=t_grad, targets=None)[0]     # shape (224,224)

        overlay  = show_cam_on_image(np_img.astype(np.float32), hm, use_rgb=True)
        _, buf   = cv2.imencode(".jpg", cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
        b64      = base64.b64encode(buf).decode()
        return hm, b64
    except Exception as e:
        print(f"[Grad-CAM] failed: {e}")
        return None, None




def region_analysis(hm: np.ndarray) -> dict:
    """Which facial region did the model attend to most?"""
    h, w  = hm.shape
    top   = float(hm[:h//3,       :].mean())
    mid   = float(hm[h//3:2*h//3, :].mean())
    bot   = float(hm[2*h//3:,     :].mean())
    left  = float(hm[:, :w//2].mean())
    right = float(hm[:, w//2:].mean())
    side_bias = abs(left - right) > 0.15

    thr = 1.15  
    if   top > mid * thr and top > bot * thr:  primary = "hair/forehead"
    elif mid > top * thr and mid > bot * thr:  primary = "eyes/nose"
    elif bot > top * thr and bot > mid * thr:  primary = "mouth/jaw/chin"
    else:                                       primary = "balanced"

    notes = {
        "hair/forehead":  "Hair/forehead focus — possible hair-length stereotype",
        "eyes/nose":      "Mid-face focus — relatively gender-neutral cue",
        "mouth/jaw/chin": "Jawline/chin focus — possible jawline-shape stereotype",
        "balanced":       "Attention distributed evenly — gender-neutral",
    }
    note = notes[primary]
    if side_bias:
        note += "; side-asymmetric attention detected (profile-photo bias possible)"

    return {
        "primary_region":      primary,
        "bias_interpretation": note,
        "region_scores": {
            "top_forehead": round(top, 4),
            "mid_face":     round(mid, 4),
            "lower_face":   round(bot, 4),
        },
        "side_asymmetry": side_bias,
    }


def compute_per_image_bias_score(pred_label: str, confidence: float,
                                  hm) -> float:
   
    disp    = fairness.get("disparity", {})
    tpr_gap = disp.get("max_tpr_gap", 0.0)
    acc_gap = disp.get("max_accuracy_gap", 0.0)

    base         = min((tpr_gap + acc_gap) / 2.0, 0.5)
    conf_penalty = max(0.0, confidence - 0.85) * 0.6   
    act_penalty = 0.0
    if hm is not None:
        ra          = region_analysis(hm)
        act_penalty = {
            "hair/forehead":  0.22,
            "mouth/jaw/chin": 0.16,
            "eyes/nose":      0.06,
            "balanced":       0.02,
        }.get(ra["primary_region"], 0.02)
        if ra["side_asymmetry"]:
            act_penalty += 0.05

    
    groups       = fairness.get("by_group", {})
    class_weight = 1.0
    if pred_label == "Female" and groups:
        female_acc   = groups.get("Female", {}).get("accuracy", 1.0)
  
        class_weight = 1.0 + max(0.0, 1.0 - female_acc)

    return round(min((base + conf_penalty + act_penalty) * class_weight, 1.0), 4)


def bias_assessment(pred: str, conf: float, hm=None) -> dict:
    """Full per-image bias report."""
    disp    = fairness.get("disparity", {})
    tpr_gap = disp.get("max_tpr_gap", 0.0)
    acc_gap = disp.get("max_accuracy_gap", 0.0)

    risk_score = compute_per_image_bias_score(pred, conf, hm)
    risk       = "high" if risk_score > 0.45 else "medium" if risk_score > 0.20 else "low"

    groups = fairness.get("by_group", {})

    
    affected = ([g for g, v in groups.items() if v.get("accuracy", 1.0) < 0.85]
                if pred == "Female" else [])

    expl = [
        f"Prediction: {pred} (confidence {conf:.1%}).",
        f"Model-level TPR gap: {tpr_gap:.3f}, accuracy gap: {acc_gap:.3f}.",
    ]
    if pred == "Female":
        f_acc = groups.get("Female", {}).get("accuracy", 1.0)
        m_acc = groups.get("Male",   {}).get("accuracy", 1.0)
        expl.append(
            f"Female group accuracy is only {f_acc:.1%} vs Male {m_acc:.1%} — "
            "a {:.1%} gap demonstrating strong demographic bias.".format(m_acc - f_acc)
        )
    if conf > 0.90:
        expl.append(
            "Very high prediction confidence may indicate reliance on a stereotyped visual shortcut."
        )

    act = None
    if hm is not None:
        act = region_analysis(hm)
        expl.append(act["bias_interpretation"] + ".")

    recs = {
        "high":   ("Immediate action required: audit training data for demographic balance; "
                   "apply reweighting, adversarial debiasing, or Fairlearn post-processing."),
        "medium": "Fine-tune with demographically balanced data; monitor per-group TPR after each epoch.",
        "low":    "Model appears relatively fair for this prediction; continue routine periodic audits.",
    }

    return {
        "bias_risk":           risk,
        "risk_score":          risk_score,
        "affected_groups":     affected,
        "explanation":         " ".join(expl),
        "recommendation":      recs[risk],
        "disparity_metrics":   {
            "max_tpr_gap":      round(tpr_gap, 3),
            "max_accuracy_gap": round(acc_gap, 3),
        },
        "activation_analysis": act,
    }




@app.get("/")
def home():
    return {
        "service":       "CV Bias Scanner",
        "model_overall": fairness.get("overall", {}),
        "disparity":     fairness.get("disparity", {}),
        "endpoints":     ["/scan", "/predict", "/audit",
                          "/bias-summary", "/high-risk-groups", "/group-metrics"],
    }


@app.get("/bias-summary")
def bias_summary():
    disp    = fairness.get("disparity", {})
    overall = fairness.get("overall", {})
    tpr_gap = disp.get("max_tpr_gap", 0.0)
    return {
        "max_tpr_gap":      tpr_gap,
        "max_accuracy_gap": disp.get("max_accuracy_gap", 0.0),
        "overall_accuracy": overall.get("accuracy", 0.0),
        "status":           ("High Bias" if tpr_gap > 0.1 else
                             "Moderate"  if tpr_gap > 0.05 else "Low Bias"),
    }


@app.get("/high-risk-groups")
def high_risk():
    g = fairness["by_group"]
    return {
        "lowest_tpr":      [{"group": k, "tpr": v["tpr"]}
                            for k, v in sorted(g.items(), key=lambda x: x[1]["tpr"])[:3]],
        "lowest_accuracy": [{"group": k, "accuracy": v["accuracy"]}
                            for k, v in sorted(g.items(), key=lambda x: x[1]["accuracy"])[:3]],
    }


@app.get("/group-metrics")
def group_metrics():
    return fairness["by_group"]


@app.get("/metrics")
def metrics():
    return fairness


@app.get("/disparity")
def disparity():
    return fairness["disparity"]


@app.post("/scan")
async def scan(file: UploadFile = File(...), view: str = Query("json")):
    img, raw, np_img, probs, pred = await _process_image(file)
    label     = "Female" if pred else "Male"
    conf      = float(probs[pred])
    group_acc = (fairness.get("by_group", {}).get(label, {}).get("accuracy")
                 or fairness.get("overall", {}).get("accuracy", 0.0))

    hm, heat_b64 = _run_gradcam(raw, np_img)  
    bias         = bias_assessment(label, conf, hm)

    if view == "html":
        _, obuf    = cv2.imencode(".jpg", cv2.cvtColor(
            (np_img * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
        orig_b64   = base64.b64encode(obuf).decode()
        risk_color = {"high": "red", "medium": "orange", "low": "green"}[bias["bias_risk"]]
        gradcam_section = (
            f"<img src='data:image/jpeg;base64,{heat_b64}' style='width:224px;border-radius:6px'>"
            if heat_b64 else
            "<p style='color:#999;font-style:italic'>Grad-CAM unavailable</p>"
        )
        act_region = (bias["activation_analysis"]["primary_region"]
                      if bias["activation_analysis"] else "N/A")
        return HTMLResponse(f"""<html><body style='font-family:Arial;margin:20px'>
        <h1>CV Bias Scan Report</h1>
        <div style='display:flex;gap:30px;align-items:flex-start'>
          <div><h3>Original Image</h3>
            <img src='data:image/jpeg;base64,{orig_b64}' style='width:224px;border-radius:6px'></div>
          <div><h3>Grad-CAM Attention Map</h3>{gradcam_section}</div>
        </div>
        <h2>Prediction: <b>{label}</b>
          &nbsp;<span style='color:{risk_color};font-size:0.9em'>
            ● {bias['bias_risk'].upper()} BIAS RISK</span>
        </h2>
        <table style='border-collapse:collapse;font-size:14px'>
          <tr><td style='padding:4px 12px'><b>Confidence</b></td><td>{conf:.2%}</td></tr>
          <tr><td style='padding:4px 12px'><b>Bias Risk Score</b></td>
              <td style='color:{risk_color}'>{bias['risk_score']:.3f} / 1.000</td></tr>
          <tr><td style='padding:4px 12px'><b>Group Accuracy</b></td>
              <td>{group_acc:.2%}</td></tr>
          <tr><td style='padding:4px 12px'><b>Primary Attention</b></td>
              <td>{act_region}</td></tr>
          <tr><td style='padding:4px 12px'><b>TPR Gap</b></td>
              <td>{bias['disparity_metrics']['max_tpr_gap']:.3f}</td></tr>
          <tr><td style='padding:4px 12px'><b>Accuracy Gap</b></td>
              <td>{bias['disparity_metrics']['max_accuracy_gap']:.3f}</td></tr>
        </table>
        <p style='max-width:640px;margin-top:16px'>{bias['explanation']}</p>
        <p style='max-width:640px'><b>Recommendation:</b> {bias['recommendation']}</p>
        </body></html>""")

    return {
        "prediction":        label,
        "confidence":        round(conf, 4),
        "group_accuracy":    round(group_acc, 4),
        "probabilities":     {"Male":   round(float(probs[0]), 4),
                              "Female": round(float(probs[1]), 4)},
        "bias_assessment":   bias,
        "heatmap_base64":    heat_b64,
        "gradcam_available": heat_b64 is not None,
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    _, raw, np_img, probs, pred = await _process_image(file)
    label     = "Female" if pred else "Male"
    conf      = float(probs[pred])
    hm, _     = _run_gradcam(raw, np_img)
    bias      = bias_assessment(label, conf, hm)
    group_acc = (fairness.get("by_group", {}).get(label, {}).get("accuracy")
                 or fairness.get("overall", {}).get("accuracy", 0.0))
    return {
        "prediction":     label,
        "confidence":     round(conf, 4),
        "group_accuracy": round(group_acc, 4),
        "bias_flag":      bias["bias_risk"],
        "risk_score":     bias["risk_score"],
        "explanation":    bias["explanation"],
        "recommendation": bias["recommendation"],
    }


@app.post("/audit")
async def audit(file: UploadFile = File(...)):
    img, raw, np_img, probs, pred = await _process_image(file)
    label     = "Female" if pred else "Male"
    conf      = float(probs[pred])
    group_acc = (fairness.get("by_group", {}).get(label, {}).get("accuracy")
                 or fairness.get("overall", {}).get("accuracy", 0.0))

    hm, _    = _run_gradcam(raw, np_img)
   
    b64_png  = None
    if hm is not None:
        overlay  = show_cam_on_image(np_img.astype(np.float32), hm, use_rgb=True)
        _, pbuf  = cv2.imencode(".png", cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
        b64_png  = base64.b64encode(pbuf).decode()

    bias       = bias_assessment(label, conf, hm)
    act_region = (bias["activation_analysis"]["primary_region"]
                  if bias["activation_analysis"] else None)

    return {
        "audit_report": {
            "prediction":            label,
            "confidence":            round(conf, 4),
            "group_accuracy":        round(group_acc, 4),
            "bias_risk_level":       bias["bias_risk"],
            "risk_score":            bias["risk_score"],
            "bias_explanation":      bias["explanation"],
            "recommendation":        bias["recommendation"],
            "affected_demographics": bias["affected_groups"],
            "activation_region":     act_region,
        },
        "heatmap_base64":    b64_png,
        "gradcam_available": b64_png is not None,
        "fairness_context":  {
            "max_tpr_gap":      bias["disparity_metrics"]["max_tpr_gap"],
            "max_accuracy_gap": bias["disparity_metrics"]["max_accuracy_gap"],
        },
    }