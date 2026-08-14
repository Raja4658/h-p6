from fastapi import FastAPI, HTTPException
import uvicorn
from contextlib import asynccontextmanager

from schemas import EvaluationRequest, EvaluationResponse
from ai_engine import AIEngine
from duplicate_checker import DuplicateChecker

# Global instances (will be initialized on startup)
ai_engine = None
duplicate_checker = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    global ai_engine, duplicate_checker
    try:
        ai_engine = AIEngine()
        duplicate_checker = DuplicateChecker()
    except Exception as e:
        print(f"Error during startup initialization: {e}")
    yield
    # Shutdown logic
    pass

app = FastAPI(
    title="Lightweight Model for Assignment & Assessment Evaluation MVP",
    description="Backend API for rubric-based scoring without external APIs.",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/api/v1/health")
def health_check():
    """
    Health check endpoint to ensure the service is running.
    """
    status = "healthy" if ai_engine is not None and duplicate_checker is not None else "degraded"
    return {"status": status}

@app.post("/api/v1/evaluate", response_model=EvaluationResponse)
def evaluate_submission(request: EvaluationRequest):
    """
    Endpoint to evaluate a student's submission.
    """
    if ai_engine is None or duplicate_checker is None:
        raise HTTPException(status_code=503, detail="AI Engine is still initializing. Please try again in a moment.")

    # 1. Check for duplicates
    is_duplicate = duplicate_checker.check_duplicate(
        submission_id=request.submission_id,
        answer_text=request.answer_text
    )
    
    # 2. Evaluate using AI Engine
    score, max_score, feedback = ai_engine.evaluate_answer(
        question_id=request.question_id,
        answer_text=request.answer_text,
        rubric_id=request.rubric_id
    )
    
    # Return formatted response
    return EvaluationResponse(
        score=score,
        max_score=max_score,
        feedback=feedback,
        duplicate_flag=is_duplicate
    )

if __name__ == "__main__":
    # Run the server locally
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
