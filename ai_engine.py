import json
import os

# Try to import torch/transformers (available locally, not on Vercel)
try:
    import torch
    from transformers import pipeline
    HAS_TORCH = False # Forced to False due to low disk space
except ImportError:
    HAS_TORCH = False
    import requests

class AIEngine:
    def __init__(self):
        if HAS_TORCH:
            # Local mode: Use transformers with torch
            print("booting up transformers...")
            self.pipe = pipeline(
                "text-generation",
                model="HuggingFaceTB/SmolLM2-360M-Instruct",
                torch_dtype=torch.float32 
            )
            print("ready")
        else:
            # Vercel mode: Use HuggingFace Inference API
            self.api_token = os.getenv("HUGGINGFACE_API_TOKEN", "")
            self.model_id = "HuggingFaceTB/SmolLM2-360M-Instruct"
            self.api_url = f"https://api-inference.huggingface.co/models/{self.model_id}"
            self.headers = {"Authorization": f"Bearer {self.api_token}"}
            print("✅ AIEngine ready (HuggingFace Inference API mode)")

    def evaluate_answer(self, q_text: str, ans_text: str, r_text: str):
        
        sys_prompt = (
            "You are a strict teacher grading an exam. "
            "You MUST output a valid JSON object in exactly this format without markdown:\n"
            '{"score": <evaluate_score_out_of_10>, "max_score": 10.0, "feedback": "<short_feedback_1_sentence>"}'
        )
        
        user_prompt = f"Q: {q_text}\nRubric: {r_text}\nAns: {ans_text}\nEvaluate and give json:"
        
        try:
            if HAS_TORCH:
                # Local: Use local pipeline
                msg = [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_prompt}
                ]
                
                res = self.pipe(
                    msg,
                    max_new_tokens=75,
                    temperature=0.1,
                    do_sample=False,
                )
                
                raw_out = res[0]["generated_text"][-1]["content"].strip()
            else:
                # Vercel: Use HuggingFace API
                payload = {
                    "inputs": f"{sys_prompt}\n\n{user_prompt}",
                    "parameters": {
                        "max_new_tokens": 75,
                    }
                }
                
                response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)
                if response.status_code != 200:
                    print(f"HF API Error: {response.status_code}")
                    return 0.0, 10.0, "API error"
                
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    raw_out = result[0].get("generated_text", "").strip()
                else:
                    raw_out = str(result).strip()
            
            # Parse JSON using regex to extract object (handles cases where prompt is echoed)
            import re
            json_match = re.search(r'\{.*?\}', raw_out, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                # fallback string cleaning
                json_str = raw_out.strip()
                if json_str.startswith("```json"): json_str = json_str[7:]
                if json_str.startswith("```"): json_str = json_str[3:]
                if json_str.endswith("```"): json_str = json_str[:-3]
                
            data = json.loads(json_str.strip())
            
            return float(data.get("score", 0)), float(data.get("max_score", 10)), str(data.get("feedback", "none"))
            
        except Exception as e:
            print("parse error ->", e)
            return 0.0, 10.0, "parsing failed"

    def verify_feedback(self, r_text: str, ans_text: str, generated_feedback: str):
        """
        Stage 2 Verifier (PS2): Checks the generated feedback for contradictions or hallucinations
        against the rubric and student's answer.
        """
        import re
        
        # Local keyword verification algorithm to simulate NLI engine.
        # This acts as our lightweight "Verifier" to operate within memory limits.
        
        words = re.findall(r'\b[a-zA-Z]{6,}\b', generated_feedback.lower()) # Check significant words
        context = (r_text + " " + ans_text).lower()
        
        flagged_spans = []
        suspicious_words = 0
        
        # Words commonly used in feedback that shouldn't be flagged
        safe_words = {"because", "missing", "rubric", "answer", "student", "excellent", "provide", "details", "score", "points", "correct", "incorrect", "learning", "example", "examples", "definition"}
        
        for word in words:
            if word not in safe_words and word not in context:
                suspicious_words += 1
                start_idx = generated_feedback.lower().find(word)
                if start_idx != -1:
                    end_idx = start_idx + len(word)
                    snippet = generated_feedback[max(0, start_idx-15):min(len(generated_feedback), end_idx+15)]
                    flagged_spans.append({
                        "text": f"...{snippet}...",
                        "reason": f"Concept '{word}' not found in rubric or student answer."
                    })

        total_words = len(words) if len(words) > 0 else 1
        hallucination_prob = min(0.95, (suspicious_words / total_words) * 1.5)
        
        # Cap at 3 flags to not overwhelm UI
        flagged_spans = flagged_spans[:3]
        
        reliability_score = (1.0 - hallucination_prob) * 100.0
        
        if reliability_score > 85:
            verdict = "Trustworthy"
        elif reliability_score > 65:
            verdict = "Partially Reliable"
        else:
            verdict = "Potential Hallucination"
            
        return {
            "reliability_score": round(reliability_score, 1),
            "hallucination_probability": round(hallucination_prob, 2),
            "verdict": verdict,
            "flagged_spans": flagged_spans
        }
