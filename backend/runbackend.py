from fastapi import FastAPI, File, UploadFile,Query
from fastapi.middleware.cors import CORSMiddleware
import torch
import torch.nn as nn
from torchvision.models import resnet50
import torchvision.transforms as T
from PIL import Image
import io, json, base64, os
import numpy as np
import cv2
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image


app = FastAPI(title="CV Bias Scanner", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


model_path = os.path.join('..', 'fairness_model.pt')
results_path = os.path.join('..', 'fairness_results.json')


model = resnet50()
model.fc = nn.Linear(model.fc.in_features, 2)
model.load_state_dict(torch.load(model_path, map_location=device))
model.to(device).eval()


with open(results_path) as f:
    bias_data = json.load(f)


transform = T.Compose([
    T.Resize((224, 224)),
    T.ToTensor(),
    T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])


def detect_bias_risk(confidence: float, prediction: str) -> dict:
    """Enhanced bias assessment with multiple metrics"""
    bias_info = {
        "bias_risk": "low",
        "risk_score": 0.0,
        "affected_groups": [],
        "explanation": "",
        "demographic_parity_ratio": bias_data.get('demographic_parity', 0.78),
        "equal_opportunity_diff": bias_data.get('equal_opportunity', 0.12),
        "subgroup_accuracy_estimate": None
    }
    
    
    high_risk_groups = ['Black_Female', 'Southeast Asian_Female']
    medium_risk_groups = ['Indian_Female', 'Latino_Hispanic_Female', 'Middle Eastern_Female']
    
    if prediction == "Female":
        bias_info["risk_score"] = 0.35
        bias_info["affected_groups"] = high_risk_groups + medium_risk_groups
        
        
        if confidence < 0.80:
            bias_info["bias_risk"] = "high"
            bias_info["subgroup_accuracy_estimate"] = 0.62  # Black female accuracy
            bias_info["explanation"] = f"Model shows {bias_data['biased']['disparity']*100:.0f}% accuracy gap for minority women"
        elif confidence < 0.90:
            bias_info["bias_risk"] = "medium"
            bias_info["subgroup_accuracy_estimate"] = 0.75
            bias_info["explanation"] = "Moderate confidence - possible demographic bias"
        else:
            bias_info["bias_risk"] = "low"
            bias_info["subgroup_accuracy_estimate"] = 0.88
            bias_info["explanation"] = "High confidence prediction"
    else:
        bias_info["risk_score"] = 0.12
        bias_info["affected_groups"] = []
        bias_info["subgroup_accuracy_estimate"] = 0.92
        bias_info["explanation"] = "Model performs better on male demographics"
    
    return bias_info

def get_bias_summary() -> dict:
    """Get overall model bias summary"""
    return {
        "model_disparity": {
            "before_mitigation": round(bias_data['biased']['disparity'], 3),
            "after_mitigation": round(bias_data['fair']['disparity'], 3),
            "reduction_percent": bias_data['improvement']['percent']
        },
        "high_risk_demographics": [
            bias_data['biased']['worst_group'],
            bias_data['fair']['worst_group']
        ],
        "fairness_status": "Improved" if bias_data['fair']['disparity'] < 0.15 else "Needs Improvement"
    }



@app.get("/")
def home():
    return {
        "service": "CV Bias Scanner",
        "model_info": {
            "biased_accuracy": round(bias_data['biased']['accuracy'], 3),
            "fair_accuracy": round(bias_data['fair']['accuracy'], 3),
            "bias_reduction": f"{bias_data['improvement']['percent']:.1f}%"
        },
        "endpoints": {
            "/scan": "POST - Full bias scan of image",
            "/predict": "POST - Quick prediction only",
            "/audit": "POST - Prediction with Grad-CAM",
            "/bias-summary": "GET - Model bias statistics",
            "/high-risk-groups": "GET - Most affected demographics"
        }
    }

@app.get("/bias-summary")
def bias_summary():
    """Get overall model bias statistics"""
    return get_bias_summary()

@app.get("/high-risk-groups")
def high_risk_groups():
    """Get demographics most affected by bias"""
    return {
        "most_affected": bias_data['biased']['worst_group'],
        "accuracy_gap": round(bias_data['biased']['disparity'], 3),
        "all_affected": [
            {"group": "Black_Female", "risk_level": "high"},
            {"group": "Southeast Asian_Female", "risk_level": "high"},
            {"group": "Indian_Female", "risk_level": "medium"},
            {"group": "Latino_Hispanic_Female", "risk_level": "medium"}
        ]
    }

@app.post("/scan")
async def scan_image(file: UploadFile = File(...), view: str = Query("json")):
    img = Image.open(io.BytesIO(await file.read())).convert('RGB')
    tensor = transform(img).unsqueeze(0).to(device)
    img_np = np.array(img.resize((224, 224))) / 255.0
    
    with torch.no_grad():
        probs = torch.softmax(model(tensor), 1)[0]
        pred = probs.argmax().item()
    
    pred_label = "Female" if pred else "Male"
    conf = float(probs[pred])
    bias = detect_bias_risk(conf, pred_label)
    
    cam = GradCAM(model=model, target_layers=[model.layer4[-1]])
    heatmap = cam(input_tensor=tensor)[0]
    overlay = show_cam_on_image(img_np, heatmap, use_rgb=True)
    _, buf = cv2.imencode('.jpg', cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
    heat_b64 = base64.b64encode(buf).decode()
    
    if view == "html":
        _, obuf = cv2.imencode('.jpg', cv2.cvtColor((img_np*255).astype(np.uint8), cv2.COLOR_RGB2BGR))
        orig_b64 = base64.b64encode(obuf).decode()
        return HTMLResponse(f"""
        <html><head><style>body{{font-family:Arial;margin:20px}}.flex{{display:flex;gap:20px}}.box{{flex:1}}img{{max-width:100%}}.risk-high{{color:red}}.risk-med{{color:orange}}.risk-low{{color:green}}</style></head><body>
        <h1>Bias Scan Result</h1><div class="flex"><div class="box"><h3>Original</h3><img src="data:image/jpeg;base64,{orig_b64}"></div><div class="box"><h3>Heatmap</h3><img src="data:image/jpeg;base64,{heat_b64}"></div></div>
        <h2>Prediction: {pred_label} <span class="risk-{bias['bias_risk']}">({bias['bias_risk'].upper()})</span></h2>
        <p>Confidence: {conf:.2%} | Risk Score: {bias['risk_score']:.2f}</p>
        <p>{bias['explanation']}</p><p>Est. Subgroup Acc: {bias['subgroup_accuracy_estimate']:.0%}</p>
        <p>Model Disparity: {bias_data['biased']['disparity']:.3f} → {bias_data['fair']['disparity']:.3f} ({bias_data['improvement']['percent']:.1f}% reduction)</p>
        </body></html>""")
    
    return {
        "prediction": pred_label, "confidence": round(conf, 4),
        "probabilities": {"Male": round(float(probs[0]),4), "Female": round(float(probs[1]),4)},
        "bias_assessment": bias,
        "model_context": {"disparity_before": bias_data['biased']['disparity'], "disparity_after": bias_data['fair']['disparity'], "reduction": bias_data['improvement']['percent']},
        "heatmap_base64": heat_b64
    }

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """Quick prediction with bias flag"""
    img = Image.open(io.BytesIO(await file.read())).convert('RGB')
    tensor = transform(img).unsqueeze(0).to(device)
    
    with torch.no_grad():
        probs = torch.softmax(model(tensor), 1)[0]
        pred = probs.argmax().item()
    
    prediction = "Female" if pred else "Male"
    confidence = float(probs[pred])
    bias_risk = detect_bias_risk(confidence, prediction)
    
    return {
        "prediction": prediction,
        "confidence": round(confidence, 4),
        "bias_flag": bias_risk["bias_risk"],
        "risk_score": bias_risk["risk_score"]
    }

@app.post("/audit")
async def audit(file: UploadFile = File(...)):
    """Detailed audit with heatmap and bias analysis"""
    img = Image.open(io.BytesIO(await file.read())).convert('RGB')
    tensor = transform(img).unsqueeze(0).to(device)
    img_np = np.array(img.resize((224, 224))) / 255.0
    
    with torch.no_grad():
        probs = torch.softmax(model(tensor), 1)[0]
        pred = probs.argmax().item()
        confidence = float(probs[pred])
    
    prediction = "Female" if pred else "Male"
    bias_assessment = detect_bias_risk(confidence, prediction)
    
    
    cam = GradCAM(model=model, target_layers=[model.layer4[-1]])
    heatmap = cam(input_tensor=tensor)[0]
    overlay = show_cam_on_image(img_np, heatmap, use_rgb=True)
    _, buf = cv2.imencode('.png', cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
    b64 = base64.b64encode(buf).decode()
    
    return {
        "audit_report": {
            "prediction": prediction,
            "confidence": round(confidence, 4),
            "bias_risk_level": bias_assessment["bias_risk"],
            "bias_explanation": bias_assessment["explanation"],
            "affected_demographics": bias_assessment["affected_groups"]
        },
        "heatmap_base64": b64,
        "fairness_context": get_bias_summary()
    }

@app.get("/metrics")
def metrics():
    return bias_data

@app.get("/disparity")
def disparity():
    return {
        "before": bias_data['biased']['disparity'],
        "after": bias_data['fair']['disparity'],
        "reduction_pct": bias_data['improvement']['percent']
    }