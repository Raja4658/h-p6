import json
import torch
from transformers import pipeline

# dict acts as our fake database for MVP
DB_MOCK = {
    "q1": "What is Supervised Learning? Explain with an example.",
    "r1": "Total marks: 10. Needs definition of supervised learning (4 marks), mentioning labeled data (3 marks), and one valid example like spam detection or house price prediction (3 marks)."
}

class AIEngine:
    def __init__(self):
        print("booting up transformers...")
        self.pipe = pipeline(
            "text-generation",
            model="HuggingFaceTB/SmolLM2-360M-Instruct",
            torch_dtype=torch.float32 
        )
        print("ready")

    def evaluate_answer(self, q_id: str, ans_text: str, r_id: str):
        # grab the question and rubric from our dummy db
        question = DB_MOCK.get(q_id, "Explain the topic.")
        rubric = DB_MOCK.get(r_id, "Max 10 marks. Be relevant.")
        
        sys_prompt = (
            "You are a strict teacher grading an exam. "
            "You MUST output a valid JSON object in exactly this format without markdown:\n"
            '{"score": 8.0, "max_score": 10.0, "feedback": "your feedback here"}'
        )
        
        user_prompt = f"Q: {question}\nRubric: {rubric}\nAns: {ans_text}\nEvaluate and give json:"
        
        msg = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            res = self.pipe(
                msg,
                max_new_tokens=150,
                temperature=0.1,
                do_sample=False,
            )
            
            raw_out = res[0]["generated_text"][-1]["content"].strip()
            
            # basic clean up for json 
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
