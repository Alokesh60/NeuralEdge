#cv_service.py
import os
import uuid
import base64
import numpy as np
import cv2
from PIL import Image
from io import BytesIO

import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision import models
import json


_FAIRNESS_PATH = os.path.join(os.path.dirname(__file__),  "fairness_results.json")
with open(_FAIRNESS_PATH) as f:
    fairness = json.load(f)


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = models.resnet50(weights=None)
model.fc = nn.Linear(model.fc.in_features, 2) 

_MODEL_PATH = os.path.join(os.path.dirname(__file__),  "fairness_model.pt")
if os.path.exists(_MODEL_PATH):
    model.load_state_dict(torch.load(_MODEL_PATH, map_location=device))
    print(f"[CV Audit] Loaded fairness_model.pt from {_MODEL_PATH}")
else:
    
    print("[CV Audit] WARNING: fairness_model.pt not found — using ImageNet weights (no gender labels)")
    model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)

model.eval().to(device)

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])



def generate_gradcam(image_pil: Image.Image):
    """
    Run Grad-CAM on image_pil.
    Uses context-local hooks so concurrent requests don't share state.
    Returns: (cam ndarray 224×224 float32, pred_class int, softmax probs tensor)
    """

    _features = {}
    _gradients = {}

    def fwd_hook(module, inp, out):
        _features["val"] = out

    def bwd_hook(module, grad_in, grad_out):
        _gradients["val"] = grad_out[0]

    target_layer = model.layer4[-1]

   
    h_fwd = target_layer.register_forward_hook(fwd_hook)
    
    h_bwd = target_layer.register_full_backward_hook(bwd_hook)

    try:
        input_tensor = transform(image_pil).unsqueeze(0).to(device)
        input_tensor.requires_grad_(True)

       
        output = model(input_tensor)
        pred_class = int(output.argmax(dim=1).item())

        model.zero_grad()
        output[0, pred_class].backward()

     
        grads = _gradients["val"][0].cpu().detach().numpy()   
        fmap  = _features["val"][0].cpu().detach().numpy()    

        weights = np.mean(grads, axis=(1, 2))                
        cam = np.zeros(fmap.shape[1:], dtype=np.float32)     
        for i, w in enumerate(weights):
            cam += w * fmap[i]

        cam = np.maximum(cam, 0)
        cam = cv2.resize(cam, (224, 224))
        cam -= cam.min()
        cam /= (cam.max() + 1e-8)

        probs = torch.nn.functional.softmax(output, dim=1).detach()
        return cam, pred_class, probs

    finally:
        
        h_fwd.remove()
        h_bwd.remove()


def overlay_heatmap(original_image: Image.Image, cam: np.ndarray) -> np.ndarray:
    original = np.array(original_image.resize((224, 224)))          
    heatmap  = cv2.applyColorMap(np.uint8(255 * cam), cv2.COLORMAP_JET)
    heatmap  = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)            
    overlay  = cv2.addWeighted(original, 0.6, heatmap, 0.4, 0)
    return overlay                                                   




def _region_analysis(cam: np.ndarray) -> dict:
    h, w  = cam.shape
    top   = float(cam[:h//3,       :].mean())
    mid   = float(cam[h//3:2*h//3, :].mean())
    bot   = float(cam[2*h//3:,     :].mean())

    thr = 1.15
    if   top > mid * thr and top > bot * thr:  region = "hair/forehead"
    elif mid > top * thr and mid > bot * thr:  region = "eyes/nose"
    elif bot > top * thr and bot > mid * thr:  region = "mouth/jaw/chin"
    else:                                       region = "balanced"

    notes = {
        "hair/forehead":  "Hair/forehead focus — possible hair-length stereotype",
        "eyes/nose":      "Mid-face focus — relatively gender-neutral cue",
        "mouth/jaw/chin": "Jawline/chin focus — possible jawline-shape stereotype",
        "balanced":       "Attention distributed evenly — gender-neutral",
    }
    return {"primary_region": region, "bias_interpretation": notes[region]}


def _compute_bias_score(label: str, confidence: float, cam: np.ndarray) -> float:
    disp    = fairness.get("disparity", {})
    tpr_gap = disp.get("max_tpr_gap", 0.0)
    acc_gap = disp.get("max_accuracy_gap", 0.0)

    base = min((tpr_gap + acc_gap) / 2.0, 0.5) if (tpr_gap + acc_gap) > 0 else 0.15

    conf_penalty = max(0.0, confidence - 0.75) * 0.6  

    ra = _region_analysis(cam)
    act_penalty = {
        "hair/forehead":  0.22,
        "mouth/jaw/chin": 0.20,
        "eyes/nose":      0.10,
        "balanced":       0.05,
    }.get(ra["primary_region"], 0.05)

    groups       = fairness.get("by_group", {})
    class_weight = 1.0
    if label == "Female" and groups:
        female_acc   = groups.get("Female", {}).get("accuracy", 1.0)
        class_weight = 1.0 + max(0.0, 1.0 - female_acc)

    raw = (base + conf_penalty + act_penalty) * class_weight
    return round(min(raw, 1.0), 2) 


def _bias_report(label: str, confidence: float, cam: np.ndarray) -> dict:
    disp    = fairness.get("disparity", {})
    tpr_gap = disp.get("max_tpr_gap", 0.0)
    acc_gap = disp.get("max_accuracy_gap", 0.0)
    groups  = fairness.get("by_group", {})

    score = _compute_bias_score(label, confidence, cam)
    risk  = "HIGH" if score > 0.45 else "MEDIUM" if score > 0.20 else "LOW"

    ra = _region_analysis(cam)

   
    group_acc = groups.get(label, {}).get("accuracy",
                fairness.get("overall", {}).get("accuracy", 0.0))

   
    affected = ([g for g, v in groups.items() if v.get("accuracy", 1.0) < 0.85]
                if label == "Female" else [])


    parts = [
        f"Prediction: {label} (confidence {confidence:.1%}).",
        f"TPR gap: {tpr_gap:.3f}, accuracy gap: {acc_gap:.3f}.",
    ]
    if label == "Female":
        f_acc = groups.get("Female", {}).get("accuracy", 1.0)
        m_acc = groups.get("Male",   {}).get("accuracy", 1.0)
        parts.append(
            f"Female group accuracy {f_acc:.1%} vs Male {m_acc:.1%} "
            f"— {(m_acc - f_acc):.1%} gap indicates demographic bias."
        )
    parts.append(ra["bias_interpretation"] + ".")

    recs = {
        "HIGH":   "Immediate action: audit training data; apply reweighting or adversarial debiasing.",
        "MEDIUM": "Fine-tune with balanced data; monitor per-group TPR.",
        "LOW":    "Model appears relatively fair; continue periodic audits.",
    }

    return {
        "bias_score":       score,
        "bias_risk":        risk,
        "group_accuracy":   round(group_acc, 4),
        "affected_groups":  affected,
        "explanation":      " ".join(parts),
        "recommendation":   recs[risk],
        "activation_region": ra["primary_region"],
        "disparity_metrics": {
            "max_tpr_gap":      round(tpr_gap, 3),
            "max_accuracy_gap": round(acc_gap, 3),
        },
    }



async def run_cv_audit(file):
    try:
        contents = await file.read()
    except Exception as e:
        raise RuntimeError(f"Failed to read uploaded file: {e}")

    try:
        image = Image.open(BytesIO(contents)).convert("RGB")
    except Exception as e:
        raise RuntimeError(f"Failed to open image — ensure file is JPG or PNG: {e}")

    try:
        cam, pred_class, probs = generate_gradcam(image)
    except Exception as e:
        raise RuntimeError(f"Grad-CAM failed: {e}")

    num_classes = probs.shape[1]
    if num_classes == 2:
  
        label      = "Female" if pred_class == 1 else "Male"
        confidence = float(probs[0, pred_class].item())
    else:
       
        label      = "Unknown (ImageNet model — load fairness_model.pt for gender prediction)"
        confidence = float(probs[0, pred_class].item())

    try:
        overlay     = overlay_heatmap(image, cam)
        overlay_bgr = cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR)
        _, buffer   = cv2.imencode(".jpg", overlay_bgr)
        heatmap_b64 = base64.b64encode(buffer).decode("utf-8")
    except Exception as e:
        raise RuntimeError(f"Heatmap generation failed: {e}")

    try:
        bias = _bias_report(label, confidence, cam)
    except Exception as e:
        raise RuntimeError(f"Bias report generation failed: {e}")

    verdict = (
        "PASS" if bias["bias_risk"] == "LOW" and bias["group_accuracy"] > 0.90
        else "FAIL"
    )

    return {
        "request_id": str(uuid.uuid4()),
        "module":     "cv",
        "model_name": "resnet50-fairness" if os.path.exists(_MODEL_PATH) else "resnet50-imagenet",

        "overall": {
            "overall": {
                "accuracy":    round(bias["group_accuracy"], 2),
                "bias_score":  bias["bias_score"],
                "bias_metric": bias["bias_risk"],
                "verdict":     verdict,
            }
        },

        "heatmap_base64":    heatmap_b64,
        "gradcam_available": True,

        "prediction":   label,
        "pred_class":   pred_class,
        "confidence":   round(confidence, 3),

        "bias_report":  bias,

        "debiasing": None,
        "recommendations": [
            bias["recommendation"],
            "Collect more diverse data across demographic groups.",
        ],

        "status":  "success",
        "message": None,
    }
