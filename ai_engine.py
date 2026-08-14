import json
import torch
from transformers import pipeline

class AIEngine:
    def __init__(self):
        # Using a very small model for MVP that can run on CPU easily with Transformers
        # SmolLM2 is extremely lightweight and fast
        model_id = "HuggingFaceTB/SmolLM2-360M-Instruct"
        
        print("Initializing AI Engine with Transformers. This will download the model (~700MB)...")
        # Load the pipeline for text generation
        self.pipe = pipeline(
            "text-generation",
            model=model_id,
            torch_dtype=torch.float32 # use float32 for CPU compatibility
        )
        print("AI Engine initialized successfully!")

    def evaluate_answer(self, question_id: str, answer_text: str, rubric_id: str):
        mock_question = "Explain the process of photosynthesis."
        mock_rubric = "Max Score 10. Award points for mentioning: Light energy (2), Chloroplasts (2), Water and Carbon Dioxide (3), Glucose and Oxygen (3)."
        
        # System prompt with strict JSON instructions
        system_prompt = (
            "You are an expert AI grader. Evaluate the student's answer based on the rubric. "
            "You MUST output ONLY a valid JSON object in this format, nothing else:\n"
            '{"score": 8.0, "max_score": 10.0, "feedback": "Good answer but missed light energy."}'
        )
        
        user_prompt = (
            f"Question: {mock_question}\n"
            f"Rubric: {mock_rubric}\n"
            f"Student Answer: {answer_text}\n"
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            # Generate response
            outputs = self.pipe(
                messages,
                max_new_tokens=150,
                temperature=0.1,
                do_sample=False,
            )
            
            # Extract generated text
            content = outputs[0]["generated_text"][-1]["content"]
            
            # Clean up the output to parse JSON
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
                
            result = json.loads(content)
            
            score = float(result.get("score", 0.0))
            max_score = float(result.get("max_score", 10.0))
            feedback = str(result.get("feedback", "No feedback provided."))
            
            return score, max_score, feedback
        except Exception as e:
            print(f"Error parsing model output: {e}\nRaw output: {content if 'content' in locals() else 'None'}")
            return 0.0, 10.0, "Error generating evaluation due to model formatting issue."
