"""
AI Engine using HuggingFace Inference API (Vercel-compatible, no large models)
"""
import json
import os
import requests

class AIEngine:
    def __init__(self):
        self.api_token = os.getenv("HUGGINGFACE_API_TOKEN", "hf_placeholder")
        self.model_id = "HuggingFaceTB/SmolLM2-360M-Instruct"
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model_id}"
        self.headers = {"Authorization": f"Bearer {self.api_token}"}
        print("✅ AIEngine ready (HuggingFace API mode)")

    def evaluate_answer(self, q_text: str, ans_text: str, r_text: str):
        try:
            sys_prompt = (
                "You are a strict teacher grading an exam. "
                "You MUST output a valid JSON object in exactly this format:\n"
                '{"score": <score_out_of_10>, "max_score": 10.0, "feedback": "<one_sentence>"}'
            )
            
            user_prompt = f"Q: {q_text}\nRubric: {r_text}\nAns: {ans_text}\nEvaluate and give json:"
            
            payload = {
                "inputs": f"{sys_prompt}\n\n{user_prompt}",
                "parameters": {
                    "max_new_tokens": 75,
                    "temperature": 0.1,
                }
            }
            
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code != 200:
                print(f"API Error: {response.status_code} - {response.text}")
                return 0.0, 10.0, "API error"
            
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                raw_out = result[0].get("generated_text", "").strip()
            else:
                raw_out = str(result).strip()
            
            # Parse JSON from response
            if "```json" in raw_out:
                raw_out = raw_out.split("```json")[1].split("```")[0]
            elif "```" in raw_out:
                raw_out = raw_out.split("```")[1]
            
            data = json.loads(raw_out.strip())
            return float(data.get("score", 0)), float(data.get("max_score", 10)), str(data.get("feedback", ""))
            
        except Exception as e:
            print(f"Error: {e}")
            return 0.0, 10.0, "evaluation failed"
