# Stage 2 MVP - Assignment Evaluation Model

This is the FastAPI backend for the Stage 2 MVP of the lightweight evaluation model.

## Features
- Evaluates student answers using a local Quantized LLM (Qwen2.5-0.5B-Instruct for speed/MVP). Fits easily in < 8GB RAM.
- Detects near-duplicate submissions using `sentence-transformers`.
- Runs completely offline without any paid external APIs like OpenAI.
- Exposes standard REST endpoints.

## Prerequisites
- Python 3.9+
- C++ Build Tools (required by `llama-cpp-python` on Windows).

## Installation

1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: If `llama-cpp-python` fails to build on Windows, you might need to install Visual Studio C++ Build Tools.*

## Running the Server

Start the FastAPI development server:
```bash
uvicorn main:app --reload
```
The first time you run this, it will download the Quantized LLM (approx 350MB) and the SentenceTransformer model (approx 80MB). Subsequent runs will be much faster.

## API Endpoints

### Health Check
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/health"
```

### Evaluate Answer
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/evaluate" \
     -H "Content-Type: application/json" \
     -d '{
           "submission_id": "sub_123",
           "question_id": "q_001",
           "answer_text": "Photosynthesis is the process by which plants use sunlight, water, and carbon dioxide to create oxygen and energy in the form of sugar.",
           "rubric_id": "rubric_bio_01"
         }'
```

## Testing Duplicate Detection
Send the exact same request twice with different `submission_id`. The second response will have `"duplicate_flag": true`.
