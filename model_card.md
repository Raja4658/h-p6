# Model & Technique Card

## 1. Approach Used
The core objective of this project is to provide a **Lightweight Assignment & Assessment Evaluation** system that runs locally without relying on expensive, third-party paid APIs (like OpenAI or Anthropic). 

To achieve this, we utilized **HuggingFaceTB/SmolLM2-360M-Instruct** via the HuggingFace `transformers` pipeline. This model acts as our `AIEngine`. We provide it with a carefully engineered system prompt that acts as a "strict teacher" and evaluates the student's answer (`answer_text`) against the provided scoring criteria (`rubric_text`).

## 2. Model Details
- **Model Name:** SmolLM2-360M-Instruct
- **Architecture:** Transformer-based Large Language Model
- **Parameters:** ~360 Million
- **Provider:** HuggingFaceTB
- **Task:** Text Generation (Instruction Tuned)

## 3. Resource Footprint
One of the primary constraints of this hackathon is that the system must run on standard institutional hardware (≤ 8 GB RAM). 
- **Memory (RAM) Requirement:** ~1.5 GB to 2 GB for loading the 360M parameter model in FP32/FP16. 
- **Compute:** Can comfortably run on a standard CPU within seconds, but is heavily accelerated if a basic GPU is available.
- **Cost:** $0 per request (100% open-source and local).

## 4. Known Limitations
- **Context Window:** Smaller models have limited context windows. Extremely long descriptive answers (e.g., spanning multiple pages) might be truncated or cause memory issues if not batched.
- **Nuance & Reasoning:** While 360M models are excellent at following basic rubrics and extracting keywords, they may occasionally miss highly abstract or philosophical nuances in student answers compared to massive 70B+ parameter models.
- **Output Formatting:** Local lightweight models occasionally fail to strictly output JSON format. We mitigated this by adding custom regex/string-cleanup functions in `ai_engine.py` to ensure robust API responses.

## 5. Duplicate / Plagiarism Detection
We implemented a dedicated `DuplicateChecker` module that compares the current submission against previous submissions to flag potential copying or near-duplicate text, ensuring academic integrity.

### Duplicate Detection Details:
- **Model:** Sentence-Transformers (all-MiniLM-L6-v2)
- **Method:** Cosine similarity on semantic embeddings
- **Threshold:** 0.85 (flags submissions with 85%+ similarity)
- **Storage:** In-memory submission history (session-based)
- **Performance:** O(n) comparison per new submission, where n = number of prior submissions

## 6. System Architecture

### Data Flow:
```
Instructor Dashboard (Streamlit)
        ↓ POST /api/v1/evaluate
FastAPI Backend (main.py)
        ↓
    Duplicate Check → DuplicateChecker (all-MiniLM-L6-v2)
        ↓ (if not plagiarism)
    AI Evaluation → AIEngine (SmolLM2-360M-Instruct)
        ↓ (JSON with score, feedback)
Streamlit Dashboard (Display Results + Override)
```

### Components:
1. **Streamlit Dashboard (dashboard.py)**
   - Question input
   - Rubric definition
   - Answer submission
   - Results visualization
   - Score override capability

2. **FastAPI Backend (main.py)**
   - `/api/v1/health` - system status
   - `/api/v1/evaluate` - process submissions
   - Request validation via Pydantic schemas
   - Mock database for fallback Q&A

3. **AI Engine (ai_engine.py)**
   - Loads SmolLM2-360M model on startup
   - Formats system + user prompts
   - Parses JSON output from model
   - Handles markdown-wrapped JSON cleanup
   - Returns: (score, max_score, feedback)

4. **Duplicate Checker (duplicate_checker.py)**
   - Maintains in-memory embedding history
   - Thread-safe using locks
   - Compares new submissions to all prior ones
   - Returns boolean duplicate flag

## 7. Scoring Methodology

### Prompt Structure:
**System Prompt:**
```
You are a strict teacher grading an exam.
You MUST output a valid JSON object in exactly this format without markdown:
{"score": <evaluate_score_out_of_10>, "max_score": 10.0, "feedback": "<short_feedback_1_sentence>"}
```

**User Prompt:**
```
Q: {question_text}
Rubric: {rubric_criteria}
Ans: {student_answer}
Evaluate and give json:
```

### Generation Settings:
- **Temperature:** 0.1 (low randomness, deterministic)
- **Max Tokens:** 75 (concise output)
- **Sampling:** Greedy (do_sample=False)
- **Timeout:** Per-request evaluation ~2-5 seconds (CPU)

### Output Processing:
- Parse JSON from model response
- Strip markdown wrappers (```json```, etc.)
- Extract: score, max_score, feedback
- Fallback on error: score=0.0, feedback="parsing failed"

## 8. Performance & Benchmarking (Stage 3)

### Expected Metrics:
- **Scoring Accuracy:** Target 85%+ agreement with human graders
- **Inference Speed:** 2-5 seconds per answer (CPU), <1s with GPU
- **Memory Usage:** ~2.5 GB total (fits 8GB constraint)
- **Duplicate Detection F1:** Target >95% on planted copy submissions
- **API Response Time:** <6 seconds end-to-end (p95)

### Evaluation Harness:
Provided by hackathon organizers with:
- Benchmark assignment set (human-graded)
- Rubrics for multiple subjects
- Sample answers of varying quality
- Automated agreement scoring

## 9. Known Limitations & Future Work

### Current Limitations:
1. **In-Memory Storage:** Duplicate history lost on server restart → use database for production
2. **Feedback Truncation:** Limited to 40 characters for dashboard display
3. **Single Subject (MVP):** Currently only biology/supervised learning example
4. **No Multi-format Support:** Text-only input (image/audio/video need preprocessing)
5. **Rubric Rigidity:** Assumes numeric 0-10 scoring; doesn't support multi-level rubrics
6. **Language:** English-only (model trained on English text)

### Path to Production (Stage 3+):
- [ ] Database-backed duplicate detection (PostgreSQL/MongoDB)
- [ ] Multi-subject rubric templates (STEM, humanities, skills)
- [ ] OCR preprocessing for scanned images
- [ ] Audio transcription support
- [ ] Fine-tuning SmolLM2 on education datasets
- [ ] Explainability features (highlight which rubric criteria met/unmet)
- [ ] Batch processing endpoint for bulk submissions
- [ ] Multi-language support
- [ ] Role-based access control for instructors/admins

## 10. Deployment & Compliance

### Deployment:
- **Docker:** Dockerfile + docker-compose.yml provided
- **Single Command:** `docker-compose up` starts all services
- **Ports:** API on 8000, Dashboard on 8501

### Data Privacy:
- ✅ All processing local (no external APIs)
- ✅ No student data sent to third parties
- ✅ Submissions stored only in memory (can add persistent DB)
- ✅ No model training on student data

### Compliance:
- No personally identifiable information (PII) processing beyond submission content
- Follows educational fairness principles
- Instructor override ensures human-in-the-loop control

---

**Version:** 0.1.0 (Stage 2 MVP)  
**Last Updated:** September 1, 2026  
**Status:** Ready for Stage 3 Evaluation
