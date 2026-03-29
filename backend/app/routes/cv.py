from fastapi import APIRouter, UploadFile
from app.services.cv_service import run_cv_audit

router = APIRouter(prefix="/audit/cv", tags=["CV"])

@router.post("/")
async def audit_cv(file: UploadFile):
    result = await run_cv_audit(file)
    return result