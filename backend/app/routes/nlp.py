from fastapi import APIRouter, UploadFile
from app.services.nlp_service import run_nlp_audit

router = APIRouter(prefix="/audit/nlp", tags=["NLP"])

@router.post("/")
async def audit_nlp(file: UploadFile):
    result = await run_nlp_audit(file)
    return result