import uuid
import base64
import numpy as np
import cv2
from PIL import Image
from io import BytesIO

import torch
import torchvision.transforms as transforms
from torchvision import models


# 🔥 Load model once (IMPORTANT)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
model.eval().to(device)

# Hook storage
features = None
gradients = None


def forward_hook(module, input, output):
    global features
    features = output


def backward_hook(module, grad_in, grad_out):
    global gradients
    gradients = grad_out[0]


# Register hooks on last conv layer
target_layer = model.layer4[-1]
target_layer.register_forward_hook(forward_hook)
target_layer.register_backward_hook(backward_hook)


# 🔥 Preprocessing
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


def generate_gradcam(image_pil):
    global features, gradients

    input_tensor = transform(image_pil).unsqueeze(0).to(device)

    # Forward
    output = model(input_tensor)
    pred_class = output.argmax(dim=1)

    # Backward
    model.zero_grad()
    output[0, pred_class].backward()

    # Grad-CAM
    grads = gradients[0].cpu().data.numpy()
    fmap = features[0].cpu().data.numpy()

    weights = np.mean(grads, axis=(1, 2))
    cam = np.zeros(fmap.shape[1:], dtype=np.float32)

    for i, w in enumerate(weights):
        cam += w * fmap[i]

    cam = np.maximum(cam, 0)
    cam = cv2.resize(cam, (224, 224))
    cam = cam - np.min(cam)
    cam = cam / (np.max(cam) + 1e-8)

    return cam, pred_class.item(), output


def overlay_heatmap(original_image, cam):
    original = np.array(original_image.resize((224, 224)))
    heatmap = cv2.applyColorMap(np.uint8(255 * cam), cv2.COLORMAP_JET)

    overlay = cv2.addWeighted(original, 0.6, heatmap, 0.4, 0)
    return overlay


async def run_cv_audit(file):
    contents = await file.read()

    image = Image.open(BytesIO(contents)).convert("RGB")

    # 🔥 Grad-CAM
    cam, pred_class, output = generate_gradcam(image)

    # Overlay
    overlay = overlay_heatmap(image, cam)

    # Encode
    _, buffer = cv2.imencode('.jpg', overlay)
    heatmap_base64 = base64.b64encode(buffer).decode("utf-8")

    # Confidence
    probs = torch.nn.functional.softmax(output, dim=1)
    confidence = probs[0, pred_class].item()

    return {
        "request_id": str(uuid.uuid4()),
        "module": "cv",
        "model_name": "resnet50-gradcam",

        "overall": {
            "overall": {
            "accuracy": round(confidence, 2),
            "bias_score": None,
            "bias_metric": "Not computable for single image",
            "verdict": "PASS" if confidence > 0.5 else "FAIL"
        },
        },

        "heatmap_base64": heatmap_base64,

        "prediction": int(pred_class),
        "confidence": round(confidence, 3),

        "debiasing": None,
        "recommendations": ["Collect more diverse data"],

        "status": "success",
        "message": None
    }