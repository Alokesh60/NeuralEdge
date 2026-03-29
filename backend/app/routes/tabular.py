from fastapi import APIRouter, UploadFile
from app.services.tabular_service import run_tabular_audit

router = APIRouter(prefix="/audit/tabular", tags=["Tabular"])

@router.post("/")
async def audit_tabular(file: UploadFile):
    result = await run_tabular_audit(file)
    return result