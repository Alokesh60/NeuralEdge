# combined.py
from fastapi import APIRouter, UploadFile
# FIX: was "from backend.app.routes.services import tabular_service" — wrong root.
# Also removed "from nlp_service import nlp_service" since nlp is on Hugging Face,
# not inside this backend. Wire it in via HTTP call when you're ready.
from app.routes.services import tabular_service

router = APIRouter(prefix="/audit/all", tags=["Combined"])

@router.post("/")
async def audit_all(file: UploadFile):

    tabular = await tabular_service.run_tabular_audit(file)
    # nlp = await nlp_service.run_nlp_audit(file)   # call HF Space URL when ready
    # cv  = await cv_service.run_cv_audit(file)      # call HF Space URL when ready

    return {
        "results": [tabular]
    }