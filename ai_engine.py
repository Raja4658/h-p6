import json
import torch
from transformers import pipeline

class AIEngine:
    def __init__(self):
        print("booting up transformers...")
        self.pipe = pipeline(
            "text-generation",
            model="HuggingFaceTB/SmolLM2-360M-Instruct",
            torch_dtype=torch.float32 
        )
        print("ready")

    def evaluate_answer(self, q_text: str, ans_text: str, r_text: str):
        
        sys_prompt = (
            "You are a strict teacher grading an exam. "
            "You MUST output a valid JSON object in exactly this format without markdown:\n"
            '{"score": <evaluate_score_out_of_10>, "max_score": 10.0, "feedback": "<short_feedback_1_sentence>"}'
        )
        
        user_prompt = f"Q: {q_text}\nRubric: {r_text}\nAns: {ans_text}\nEvaluate and give json:"
        
        msg = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            res = self.pipe(
                msg,
                max_new_tokens=75,
                temperature=0.1,
                do_sample=False,
            )
            
            raw_out = res[0]["generated_text"][-1]["content"].strip()
            
            # sometimes the model spits out markdown, need to strip it before parsing
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
