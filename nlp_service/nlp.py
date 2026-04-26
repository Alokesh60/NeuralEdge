from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from nlp_service import run_nlp_audit

router = APIRouter(prefix="/audit/nlp", tags=["NLP"])

SUPPORTED_MODELS = {
    "bert-base-uncased",
    "roberta-base",
    "distilbert-base-uncased",
}

SUPPORTED_BENCHMARKS    = {"winobias", "sentiment", "toxicity"}
SUPPORTED_DEMO_GROUPS   = {"Gender", "Race", "Religion"}


class NLPAuditRequest(BaseModel):
    model_name:          Optional[str]       = "bert-base-uncased"
    benchmarks:          Optional[List[str]] = ["winobias", "sentiment", "toxicity"]
    demographic_groups:  Optional[List[str]] = ["Gender", "Race", "Religion"]


@router.post("/")
async def audit_nlp(request: NLPAuditRequest):
    model = request.model_name or "bert-base-uncased"
    if model not in SUPPORTED_MODELS:
        return {
            "status":  "error",
            "message": f"Unsupported model '{model}'. Supported: {sorted(SUPPORTED_MODELS)}",
        }

    # Sanitise — only keep recognised values sent from the frontend
    benchmarks         = [b for b in (request.benchmarks         or []) if b in SUPPORTED_BENCHMARKS]
    demographic_groups = [g for g in (request.demographic_groups or []) if g in SUPPORTED_DEMO_GROUPS]

    if not benchmarks:
        return {"status": "error", "message": "Select at least one benchmark to run."}
    if not demographic_groups:
        return {"status": "error", "message": "Select at least one demographic group."}

    result = await run_nlp_audit(
        model_name=model,
        benchmarks=benchmarks,
        demographic_groups=demographic_groups,
    )
    return result