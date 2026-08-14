from fastapi import FastAPI, HTTPException
import uvicorn
from contextlib import asynccontextmanager

from schemas import EvaluationRequest, EvaluationResponse
from ai_engine import AIEngine
from duplicate_checker import DuplicateChecker

evaluator = None
checker = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global evaluator, checker
    try:
        evaluator = AIEngine()
        checker = DuplicateChecker()
    except Exception as err:
        print("startup error:", err)
    yield
    # clean up if needed

app = FastAPI(title="Vira Tech - Auto Grader API")

@app.get("/api/v1/health")
def ping():
    if evaluator and checker:
        return {"status": "ok"}
    return {"status": "starting"}

@app.post("/api/v1/evaluate", response_model=EvaluationResponse)
def grade_answer(req: EvaluationRequest):
    if not evaluator:
        raise HTTPException(status_code=503, detail="still loading ai model...")

    # check plagiarism first
    is_copied = checker.check_duplicate(req.submission_id, req.answer_text)
    
    # get marks from llm
    marks, max_marks, comments = evaluator.evaluate_answer(
        q_id=req.question_id,
        ans_text=req.answer_text,
        r_id=req.rubric_id
    )
    
    return EvaluationResponse(
        score=marks,
        max_score=max_marks,
        feedback=comments,
        duplicate_flag=is_copied
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
