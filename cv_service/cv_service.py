import os
import uuid
import base64
import numpy as np
import cv2
from PIL import Image
from io import BytesIO
import json

import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision import models

# Paths
_BASE_DIR = os.path.dirname(__file__)
_FAIRNESS_PATH = os.path.join(_BASE_DIR, "fairness_results.json")
_MODEL_PATH = os.path.join(_BASE_DIR, "fairness_model.pt")

# Globals (lazy loaded)
model = None
fairness = {}

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# -------------------------
# Lazy Load Functions
# -------------------------

def load_fairness():
    global fairness
    if not fairness:
        if os.path.exists(_FAIRNESS_PATH):
            with open(_FAIRNESS_PATH) as f:
                fairness = json.load(f)
        else:
            print("[CV] fairness_results.json not found, using defaults")
            fairness = {}

def get_model():
    global model
    if model is None:
        print("[CV] Loading model...")

        m = models.resnet50(weights=None)
        m.fc = nn.Linear(m.fc.in_features, 2)

        if os.path.exists(_MODEL_PATH):
            m.load_state_dict(torch.load(_MODEL_PATH, map_location=device))
            print("[CV] Loaded fairness_model.pt")
        else:
            print("[CV] Using ImageNet weights (fallback)")
            m = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)

        m.eval().to(device)
        model = m

    return model


# -------------------------
# Transform
# -------------------------

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# -------------------------
# GradCAM
# -------------------------

def generate_gradcam(image_pil: Image.Image):
    model = get_model()

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
        fmap = _features["val"][0].cpu().detach().numpy()

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


# -------------------------
# Utility Functions
# -------------------------

def overlay_heatmap(original_image: Image.Image, cam: np.ndarray):
    original = np.array(original_image.resize((224, 224)))
    heatmap = cv2.applyColorMap(np.uint8(255 * cam), cv2.COLORMAP_JET)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
    return cv2.addWeighted(original, 0.6, heatmap, 0.4, 0)


def _region_analysis(cam):
    h, w = cam.shape
    top = float(cam[:h//3].mean())
    mid = float(cam[h//3:2*h//3].mean())
    bot = float(cam[2*h//3:].mean())

    if top > mid and top > bot:
        return "hair/forehead"
    elif mid > top and mid > bot:
        return "eyes/nose"
    elif bot > top and bot > mid:
        return "mouth/jaw/chin"
    return "balanced"


def _compute_bias_score(label, confidence, cam):
    load_fairness()

    disp = fairness.get("disparity", {})
    tpr_gap = disp.get("max_tpr_gap", 0.0)
    acc_gap = disp.get("max_accuracy_gap", 0.0)

    base = min((tpr_gap + acc_gap) / 2.0, 0.5) if (tpr_gap + acc_gap) > 0 else 0.15
    conf_penalty = max(0.0, confidence - 0.75) * 0.6

    region = _region_analysis(cam)

    act_penalty = {
        "hair/forehead": 0.22,
        "mouth/jaw/chin": 0.20,
        "eyes/nose": 0.10,
        "balanced": 0.05,
    }.get(region, 0.05)

    return round(min(base + conf_penalty + act_penalty, 1.0), 2)


def _bias_report(label, confidence, cam):
    score = _compute_bias_score(label, confidence, cam)

    return {
        "bias_score": score,
        "bias_risk": "HIGH" if score > 0.45 else "MEDIUM" if score > 0.2 else "LOW",
        "activation_region": _region_analysis(cam)
    }


# -------------------------
# Main API Function
# -------------------------

async def run_cv_audit(file):
    contents = await file.read()
    image = Image.open(BytesIO(contents)).convert("RGB")

    cam, pred_class, probs = generate_gradcam(image)

    label = "Female" if pred_class == 1 else "Male"
    confidence = float(probs[0, pred_class].item())

    overlay = overlay_heatmap(image, cam)
    overlay_bgr = cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR)
    _, buffer = cv2.imencode(".jpg", overlay_bgr)
    heatmap_b64 = base64.b64encode(buffer).decode("utf-8")

    bias = _bias_report(label, confidence, cam)

    return {
        "request_id": str(uuid.uuid4()),
        "module": "cv",
        "prediction": label,
        "confidence": round(confidence, 3),
        "bias_report": bias,
        "heatmap_base64": heatmap_b64,
        "status": "success"
    }
