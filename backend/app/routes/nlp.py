from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.services.nlp_service import run_nlp_audit

router = APIRouter(prefix="/audit/nlp", tags=["NLP"])

# Allowed fill-mask models (WinoBias test)
SUPPORTED_MODELS = {
    "bert-base-uncased",
    "roberta-base",
    "distilbert-base-uncased",
}

class NLPAuditRequest(BaseModel):
    model_name: Optional[str] = "bert-base-uncased"

@router.post("/")
async def audit_nlp(request: NLPAuditRequest):
    model = request.model_name or "bert-base-uncased"
    if model not in SUPPORTED_MODELS:
        return {
            "status": "error",
            "message": f"Unsupported model '{model}'. Supported: {sorted(SUPPORTED_MODELS)}"
        }
    result = await run_nlp_audit(model_name=model)
    return result