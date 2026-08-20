import requests
import json

# The API URL
url = "http://127.0.0.1:8000/api/v1/evaluate"

# The Request Data
payload = {
    "submission_id": "sub_1",
    "question_text": "What is Supervised Learning? Explain with an example.",
    "answer_text": "Supervised learning is a machine learning method where models are trained using labeled data. For example, predicting house prices based on historical data.",
    "rubric_text": "Total marks: 10. Needs definition of supervised learning (4 marks), mentioning labeled data (3 marks), and one valid example like spam detection or house price prediction (3 marks)."
}

print("Sending Request to API...")
print(json.dumps(payload, indent=2))
print("-" * 40)

# Send POST request
try:
    response = requests.post(url, json=payload)
    print("\nAPI Response:")
    
    # Format and print the output exactly like the problem statement
    formatted_response = json.dumps(response.json(), indent=2)
    print(formatted_response)
    
except Exception as e:
    print(f"Error: Make sure the server (uvicorn) is running! Details: {e}")
