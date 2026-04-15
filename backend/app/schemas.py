from pydantic import BaseModel
from typing import List, Dict, Optional

class GroupMetric(BaseModel):
    group_name: str
    metrics: Dict[str, float]

class Explanation(BaseModel):
    type: str
    description: str
    image_base64: Optional[str]

class Debiasing(BaseModel):
    method: str
    before_score: float
    after_score: float
    improvement: float

class ResponseSchema(BaseModel):
    request_id: str
    module: str
    model_name: str

    overall: Dict[str, float | str]
    groups: List[GroupMetric]

    explanation: Optional[Explanation]
    debiasing: Optional[Debiasing]

    recommendations: List[str]

    status: str
    message: Optional[str]

from pydantic import BaseModel
from typing import List, Dict, Optional

# ... (keep your existing ResponseSchema and others) ...

class FlexibleAuditRequest(BaseModel):
    target_column: str
    sensitive_columns: List[str]
    privileged_groups: Dict[str, str]
    model_choice: str = "logistic"
    # model_file is handled via UploadFile separately

class FlexibleAuditResponse(ResponseSchema):
    # same structure as before
    pass


class ExplanationSummary(BaseModel):
    verdict_explanation: str
    suggestions: List[str]
    metric_descriptions: Dict[str, str]

class ResponseSchema(BaseModel):
    # ... existing fields ...
    explanation_summary: Optional[ExplanationSummary] = None