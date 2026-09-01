import json
import os

# Try to import torch/transformers (available locally, not on Vercel)
try:
    import torch
    from transformers import pipeline
    HAS_TORCH = True
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
            
            # Parse JSON (same for both modes)
            if raw_out.startswith("```json"):
                raw_out = raw_out[7:]
            if raw_out.startswith("```"):
                raw_out = raw_out[3:]
            if raw_out.endswith("```"):
                raw_out = raw_out[:-3]
                
            data = json.loads(raw_out.strip())
            
            return float(data.get("score", 0)), float(data.get("max_score", 10)), str(data.get("feedback", "none"))
            
        except Exception as e:
            print("parse error ->", e)
            return 0.0, 10.0, "parsing failed"
