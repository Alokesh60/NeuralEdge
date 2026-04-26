# combined.py
from fastapi import APIRouter, UploadFile
from app.services import tabular_service, nlp_service, cv_service

router = APIRouter(prefix="/audit/all", tags=["Combined"])

@router.post("/")
async def audit_all(file: UploadFile):

    tabular = await tabular_service.run_tabular_audit(file)
    nlp = await nlp_service.run_nlp_audit(file)
    cv = await cv_service.run_cv_audit(file)

    return {
        "results": [tabular, nlp, cv]
    }