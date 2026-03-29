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