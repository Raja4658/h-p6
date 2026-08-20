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
