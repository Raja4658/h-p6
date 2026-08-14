from pydantic import BaseModel

class EvaluationRequest(BaseModel):
    submission_id: str
    question_id: str
    answer_text: str
    rubric_id: str

class EvaluationResponse(BaseModel):
    score: float
    max_score: float
    feedback: str
    duplicate_flag: bool
