import requests
import json

url = "http://127.0.0.1:8000/api/v1/evaluate"

# Sending the exact same answer but from a different student (student_002)
payload = {
    "submission_id": "student_002", 
    "question_text": "What is Supervised Learning? Explain with an example.",
    "answer_text": "Supervised learning is a machine learning method where models are trained using labeled data. For example, predicting house prices.",
    "rubric_text": "Total marks: 10. Needs definition of supervised learning (4 marks), mentioning labeled data (3 marks), and one valid example like spam detection or house price prediction (3 marks)."
}

print("==== RUNNING TRUE TEST (Copied Answer) ====\n")
print(json.dumps(payload, indent=2))
print("-" * 40)

try:
    response = requests.post(url, json=payload)
    print("\nAPI Response:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
