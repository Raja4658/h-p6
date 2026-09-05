from pydantic import BaseModel

class EvaluationRequest(BaseModel):
    submission_id: str
    question_id: str
    answer_text: str
    rubric_id: str
    
    # Optional fields for dashboard testing
    question_text: str | None = None
    rubric_text: str | None = None

class ReliabilityMetrics(BaseModel):
    reliability_score: float
    hallucination_probability: float
    verdict: str
    flagged_spans: list[dict]

class EvaluationResponse(BaseModel):
    score: float
    max_score: float
    feedback: str
    duplicate_flag: bool
    reliability: ReliabilityMetrics
