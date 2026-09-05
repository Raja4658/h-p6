from fastapi import FastAPI, HTTPException
import uvicorn
from contextlib import asynccontextmanager

from schemas import EvaluationRequest, EvaluationResponse
from ai_engine import AIEngine
from duplicate_checker import DuplicateChecker

evaluator = None
checker = None

MOCK_DB = {
    "questions": {
        "q1": "What is Supervised Learning? Explain with an example."
    },
    "rubrics": {
        "r1": "Total marks: 10. Needs definition of supervised learning (4 marks), mentioning labeled data (3 marks), and one valid example like spam detection or house price prediction (3 marks)."
    }
}

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

app = FastAPI(title="Vira Tech - Auto Grader API", lifespan=lifespan)

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
    
    # get texts (use optional payload texts if provided by dashboard, else fallback to mock db)
    q_text = req.question_text or MOCK_DB["questions"].get(req.question_id, "Explain the concept.")
    r_text = req.rubric_text or MOCK_DB["rubrics"].get(req.rubric_id, "Grade out of 10.")

    # get marks from llm
    marks, max_marks, comments = evaluator.evaluate_answer(
        q_text=q_text,
        ans_text=req.answer_text,
        r_text=r_text
    )
    
    # truncate feedback so PowerShell table doesn't hide the duplicate_flag
    if len(comments) > 40:
        comments = comments[:37] + "..."
        
    # verify feedback for hallucinations (PS2 Integration)
    reliability_data = evaluator.verify_feedback(
        r_text=r_text,
        ans_text=req.answer_text,
        generated_feedback=comments
    )
        
    return EvaluationResponse(
        score=marks,
        max_score=max_marks,
        feedback=comments,
        duplicate_flag=is_copied,
        reliability=reliability_data
    )

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    try:
        uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
    except OSError:
        print(f"Port {port} in use. Trying port 8080...")
        uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
