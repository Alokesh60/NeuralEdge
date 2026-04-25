# tabular.py

# from fastapi import APIRouter, UploadFile, File, Form, HTTPException
# from typing import Optional
# from app.services.tabular_service import run_tabular_audit
# import json

# router = APIRouter(prefix="/audit/tabular", tags=["Tabular"])

# # Legacy endpoint (UCI Adult)
# @router.post("/")
# async def audit_tabular_legacy(file: UploadFile = File(...)):
#     return await run_tabular_audit(
#         file=file,
#         target_col="income",
#         sensitive_cols=["sex"],
#         privileged_groups={"sex": "Male"},
#         model_choice="logistic"
#     )

# # Flexible endpoint with optional model and preprocessor files
# @router.post("/flexible")
# async def audit_tabular_flexible(
#     file: UploadFile = File(...),
#     target_column: str = Form(...),
#     sensitive_columns: str = Form(...),
#     privileged_values: str = Form(...),
#     model_choice: str = Form("logistic"),
#     model_file: Optional[UploadFile] = File(None),
#     preprocessor_file: Optional[UploadFile] = File(None)
# ):
#     try:
#         sensitive_list = [s.strip() for s in sensitive_columns.split(",")]
#         privileged_dict = json.loads(privileged_values)
#         model_obj = None
#         preprocessor_obj = None
#         if model_file:
#             import joblib
#             model_obj = joblib.load(model_file.file)
#         if preprocessor_file:
#             import joblib
#             preprocessor_obj = joblib.load(preprocessor_file.file)
#         result = await run_tabular_audit(
#             file=file,
#             target_col=target_column,
#             sensitive_cols=sensitive_list,
#             privileged_groups=privileged_dict,
#             model_choice=model_choice,
#             model_file=model_obj,
#             preprocessor_file=preprocessor_obj
#         )
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))



from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from app.services.tabular_service import run_tabular_audit
import json

router = APIRouter(prefix="/audit/tabular", tags=["Tabular"])

# Legacy endpoint (UCI Adult) – no shap_sample_size needed
@router.post("/")
async def audit_tabular_legacy(file: UploadFile = File(...)):
    return await run_tabular_audit(
        file=file,
        target_col="income",
        sensitive_cols=["sex"],
        privileged_groups={"sex": "Male"},
        model_choice="logistic"
    )

# Flexible endpoint with optional model, preprocessor, and shap_sample_size
@router.post("/flexible")
async def audit_tabular_flexible(
    file: UploadFile = File(...),
    target_column: str = Form(...),
    sensitive_columns: str = Form(...),
    privileged_values: str = Form(...),
    model_choice: str = Form("logistic"),
    model_file: Optional[UploadFile] = File(None),
    preprocessor_file: Optional[UploadFile] = File(None),
    shap_sample_size: Optional[int] = Form(None)         # NEW: optional SHAP sample size
):
    try:
        sensitive_list = [s.strip() for s in sensitive_columns.split(",")]
        privileged_dict = json.loads(privileged_values)
        model_obj = None
        preprocessor_obj = None
        if model_file:
            import joblib
            model_obj = joblib.load(model_file.file)
        if preprocessor_file:
            import joblib
            preprocessor_obj = joblib.load(preprocessor_file.file)
        result = await run_tabular_audit(
            file=file,
            target_col=target_column,
            sensitive_cols=sensitive_list,
            privileged_groups=privileged_dict,
            model_choice=model_choice,
            model_file=model_obj,
            preprocessor_file=preprocessor_obj,
            shap_sample_size=shap_sample_size   # NEW: pass to the service
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))