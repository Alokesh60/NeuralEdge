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

def region_analysis(hm: np.ndarray) -> dict:
    h = hm.shape[0]
    top, mid, bot = hm[:h//3].mean(), hm[h//3:2*h//3].mean(), hm[2*h//3:].mean()
    regions = []
    if top > max(mid, bot)*1.2: regions.append("hair/forehead")
    if mid > max(top, bot)*1.2: regions.append("eyes/nose")
    if bot > max(top, mid)*1.2: regions.append("mouth/jaw")
    primary = regions[0] if regions else "balanced"
    note = ("hair/forehead stereotype" if "hair" in primary else
            "jawline bias" if "mouth" in primary or "jaw" in primary else
            "gender‑neutral")
    return {"primary_region": primary, "bias_interpretation": note}

def bias_assessment(pred: str, conf: float, hm: np.ndarray = None) -> dict:

    disparity_data = fairness.get("disparity") or fairness.get("disparity", {})
    tpr_gap = disparity_data.get("max_tpr_gap", 0.0)
    acc_gap = disparity_data.get("max_accuracy_gap", 0.0)

    risk = "high" if max(tpr_gap, acc_gap) > 0.15 else "medium" if max(tpr_gap, acc_gap) > 0.08 else "low"
    groups = fairness.get("by_group", {})
    
    
    if groups:
        worst_acc = min(groups.items(), key=lambda x: x[1]["accuracy"])[0]
        worst_tpr = min(groups.items(), key=lambda x: x[1]["tpr"])[0]
    else:
        worst_acc = "unknown"
        worst_tpr = "unknown"
    
    affected = [worst_acc, worst_tpr] if pred == "Female" and worst_acc != "unknown" else []
    expl = f"TPR gap {tpr_gap:.3f}, Acc gap {acc_gap:.3f}."
    if pred == "Female": expl += " Female predictions disproportionately affected."
    act = None
    if hm is not None:
        act = region_analysis(hm)
        expl += " " + act["bias_interpretation"]
    return {
        "bias_risk": risk, "risk_score": round(min(tpr_gap, 1.0), 3),
        "affected_groups": affected, "explanation": expl,
        "disparity_metrics": {"max_tpr_gap": round(tpr_gap,3), "max_accuracy_gap": round(acc_gap,3)},
        "activation_analysis": act
    }


@app.get("/")
def home():
   
    overall_data = fairness.get("overall", {})
    disparity_data = fairness.get("disparity") or fairness.get("disparity", {})
    return {
        "service": "CV Bias Scanner",
        "model_overall": overall_data,               # empty dict if missing
        "disparity": disparity_data,
        "endpoints": ["/scan", "/predict", "/audit", "/bias-summary", "/high-risk-groups", "/group-metrics"]
    }

@app.get("/bias-summary")
def bias_summary():
    disparity_data = fairness.get("disparity") or fairness.get("disparity", {})
    overall_data = fairness.get("overall", {})
    return {
        "max_tpr_gap": disparity_data.get("max_tpr_gap", 0.0),
        "max_accuracy_gap": disparity_data.get("max_accuracy_gap", 0.0),
        "overall_accuracy": overall_data.get("accuracy", 0.0),
        "status": "High Bias" if disparity_data.get("max_tpr_gap", 0.0) > 0.1 else "Moderate"
    }

@app.get("/high-risk-groups")
def high_risk():
    g = fairness["by_group"]
    tpr_sorted = sorted(g.items(), key=lambda x: x[1]["tpr"])
    acc_sorted = sorted(g.items(), key=lambda x: x[1]["accuracy"])
    return {"lowest_tpr": [{"group": k, "tpr": v["tpr"]} for k,v in tpr_sorted[:3]],
            "lowest_accuracy": [{"group": k, "accuracy": v["accuracy"]} for k,v in acc_sorted[:3]]}

@app.get("/group-metrics")
def group_metrics(): return fairness["by_group"]

@app.get("/metrics")
def metrics(): return fairness

@app.get("/disparity")
def disparity(): return fairness["disparity"]

async def _process_image(file: UploadFile):
    img = Image.open(io.BytesIO(await file.read())).convert('RGB')
    t = transform(img).unsqueeze(0).to(device)
    np_img = np.array(img.resize((224,224)))/255.0
    with torch.no_grad():
        probs = torch.softmax(model(t),1)[0]
        pred = probs.argmax().item()
    return img, t, np_img, probs, pred

@app.post("/scan")
async def scan(file: UploadFile = File(...), view: str = Query("json")):
    img, t, np_img, probs, pred = await _process_image(file)
    label = "Female" if pred else "Male"
    conf = float(probs[pred])
    cam = GradCAM(model=model, target_layers=[model.layer4[-1]])
    hm = cam(input_tensor=t)[0]
    overlay = show_cam_on_image(np_img, hm, use_rgb=True)
    _, buf = cv2.imencode('.jpg', cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
    heat_b64 = base64.b64encode(buf).decode()
    bias = bias_assessment(label, conf, hm)

    if view == "html":
        _, obuf = cv2.imencode('.jpg', cv2.cvtColor((np_img*255).astype(np.uint8), cv2.COLOR_RGB2BGR))
        orig_b64 = base64.b64encode(obuf).decode()
        return HTMLResponse(f"""<html><body style='font-family:Arial;margin:20px'>
        <h1>Bias Scan</h1><div style='display:flex;gap:20px'><div><h3>Original</h3><img src='data:image/jpeg;base64,{orig_b64}'></div>
        <div><h3>Heatmap</h3><img src='data:image/jpeg;base64,{heat_b64}'></div></div>
        <h2>Prediction: {label} <span style='color:{'red' if bias['bias_risk']=='high' else 'orange' if bias['bias_risk']=='medium' else 'green'}'>({bias['bias_risk'].upper()})</span></h2>
        <p>Confidence: {conf:.2%} | Risk Score: {bias['risk_score']:.3f}</p><p>{bias['explanation']}</p>
        <p>Activation: {bias['activation_analysis']['primary_region']}</p>
        <p>Disparity: TPR Gap={bias['disparity_metrics']['max_tpr_gap']:.3f}, Acc Gap={bias['disparity_metrics']['max_accuracy_gap']:.3f}</p>
        </body></html>""")
    return {"prediction": label, "confidence": round(conf,4),
            "probabilities": {"Male": round(float(probs[0]),4), "Female": round(float(probs[1]),4)},
            "bias_assessment": bias, "heatmap_base64": heat_b64}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    _, _, _, probs, pred = await _process_image(file)
    label = "Female" if pred else "Male"
    conf = float(probs[pred])
    bias = bias_assessment(label, conf)
    return {"prediction": label, "confidence": round(conf,4),
            "bias_flag": bias["bias_risk"], "risk_score": bias["risk_score"],
            "explanation": bias["explanation"]}

@app.post("/audit")
async def audit(file: UploadFile = File(...)):
    img, t, np_img, probs, pred = await _process_image(file)
    label = "Female" if pred else "Male"
    conf = float(probs[pred])
    cam = GradCAM(model=model, target_layers=[model.layer4[-1]])
    hm = cam(input_tensor=t)[0]
    overlay = show_cam_on_image(np_img, hm, use_rgb=True)
    _, buf = cv2.imencode('.png', cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
    b64 = base64.b64encode(buf).decode()
    bias = bias_assessment(label, conf, hm)
    return {
        "audit_report": {
            "prediction": label, "confidence": round(conf,4),
            "bias_risk_level": bias["bias_risk"], "bias_explanation": bias["explanation"],
            "affected_demographics": bias["affected_groups"],
            "activation_region": bias["activation_analysis"]["primary_region"] if bias["activation_analysis"] else None
        },
        "heatmap_base64": b64,
        "fairness_context": {
            "max_tpr_gap": bias["disparity_metrics"]["max_tpr_gap"],
            "max_accuracy_gap": bias["disparity_metrics"]["max_accuracy_gap"]
        }
    }