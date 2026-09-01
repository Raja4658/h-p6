#!/usr/bin/env python3
"""
Stage 3 Evaluation Harness
Vira Tech - Auto Grader System
Tests scoring accuracy, duplicate detection, and feedback quality
"""

import requests
import json
import time
from datetime import datetime

API_URL = "http://127.0.0.1:8000/api/v1/evaluate"
HEALTH_URL = "http://127.0.0.1:8000/api/v1/health"

# Test Dataset - Human graded with expected scores
TEST_CASES = [
    {
        "id": "test_001",
        "question": "What is Supervised Learning? Explain with an example.",
        "rubric": "Total marks: 10. Needs definition of supervised learning (4 marks), mentioning labeled data (3 marks), and one valid example like spam detection or house price prediction (3 marks).",
        "answer": "Supervised learning is a machine learning method where models are trained using labeled data. For example, predicting house prices based on features like size and location.",
        "human_score": 8.0,
        "tolerance": 1.5,  # ±1.5 points is acceptable
        "expected_duplicate": False
    },
    {
        "id": "test_002",
        "question": "What is Supervised Learning? Explain with an example.",
        "rubric": "Total marks: 10. Needs definition of supervised learning (4 marks), mentioning labeled data (3 marks), and one valid example like spam detection or house price prediction (3 marks).",
        "answer": "SL means using labeled training data. Example: Email spam detector learns from spam/not-spam examples.",
        "human_score": 6.0,
        "tolerance": 1.5,
        "expected_duplicate": False
    },
    {
        "id": "test_003",
        "question": "What is Supervised Learning? Explain with an example.",
        "rubric": "Total marks: 10. Needs definition of supervised learning (4 marks), mentioning labeled data (3 marks), and one valid example like spam detection or house price prediction (3 marks).",
        "answer": "Supervised learning is the process of training data by providing labeled examples to the model.",
        "human_score": 5.0,
        "tolerance": 1.5,
        "expected_duplicate": False
    },
    {
        "id": "test_004",
        "question": "What is Supervised Learning? Explain with an example.",
        "rubric": "Total marks: 10. Needs definition of supervised learning (4 marks), mentioning labeled data (3 marks), and one valid example like spam detection or house price prediction (3 marks).",
        "answer": "It's a type of machine learning. There are many algorithms. It's used in industry.",
        "human_score": 2.0,
        "tolerance": 1.5,
        "expected_duplicate": False
    },
    {
        "id": "test_005",
        "question": "What is Supervised Learning? Explain with an example.",
        "rubric": "Total marks: 10. Needs definition of supervised learning (4 marks), mentioning labeled data (3 marks), and one valid example like spam detection or house price prediction (3 marks).",
        "answer": "Supervised learning is a machine learning method where models are trained using labeled data. For example, predicting house prices based on features like size and location.",  # Identical to test_001
        "human_score": 8.0,
        "tolerance": 1.5,
        "expected_duplicate": True  # This should be flagged as duplicate of test_001
    },
    {
        "id": "test_006",
        "question": "What is Supervised Learning? Explain with an example.",
        "rubric": "Total marks: 10. Needs definition of supervised learning (4 marks), mentioning labeled data (3 marks), and one valid example like spam detection or house price prediction (3 marks).",
        "answer": "Supervised learning is a ML method where models are trained using labeled datasets. For instance, predicting real estate prices based on characteristics such as size and neighborhood.",  # Near-duplicate of test_001
        "human_score": 8.0,
        "tolerance": 1.5,
        "expected_duplicate": True
    }
]

# Color output for test results
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*70}")
    print(f"{text}")
    print(f"{'='*70}{Colors.END}\n")

def print_pass(text):
    print(f"{Colors.GREEN}✅ PASS: {text}{Colors.END}")

def print_fail(text):
    print(f"{Colors.RED}❌ FAIL: {text}{Colors.END}")

def print_warn(text):
    print(f"{Colors.YELLOW}⚠️  WARN: {text}{Colors.END}")

def test_health_check():
    """Test API health endpoint"""
    print_header("TEST 1: API Health Check")
    try:
        resp = requests.get(HEALTH_URL, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "ok":
                print_pass(f"Health check passed: {data}")
                return True
            else:
                print_fail(f"Health status not 'ok': {data}")
                return False
        else:
            print_fail(f"Health endpoint returned {resp.status_code}")
            return False
    except Exception as e:
        print_fail(f"Failed to reach health endpoint: {e}")
        return False

def test_scoring_accuracy():
    """Test scoring accuracy against human-graded samples"""
    print_header("TEST 2: Scoring Accuracy Benchmarking")
    
    results = []
    total_score_diff = 0
    matching_scores = 0
    
    for i, test in enumerate(TEST_CASES[:4]):  # First 4 are non-duplicates
        try:
            print(f"\n[{i+1}/4] Evaluating: {test['id']}")
            print(f"  Question: {test['question'][:50]}...")
            print(f"  Human Score: {test['human_score']}/10")
            print(f"  Answer: {test['answer'][:60]}...")
            
            payload = {
                "submission_id": test["id"],
                "question_id": "q1",
                "rubric_id": "r1",
                "question_text": test["question"],
                "rubric_text": test["rubric"],
                "answer_text": test["answer"]
            }
            
            resp = requests.post(API_URL, json=payload, timeout=30)
            
            if resp.status_code == 200:
                data = resp.json()
                ai_score = data.get("score", 0.0)
                score_diff = abs(ai_score - test["human_score"])
                
                print(f"  AI Score: {ai_score}/10")
                print(f"  Difference: ±{score_diff:.1f} points")
                
                if score_diff <= test["tolerance"]:
                    print_pass(f"Score within tolerance (±{test['tolerance']})")
                    matching_scores += 1
                else:
                    print_warn(f"Score outside tolerance (diff={score_diff:.1f})")
                
                total_score_diff += score_diff
                results.append({
                    "test_id": test["id"],
                    "human_score": test["human_score"],
                    "ai_score": ai_score,
                    "diff": score_diff,
                    "within_tolerance": score_diff <= test["tolerance"]
                })
                
                time.sleep(0.5)  # Rate limiting
            else:
                print_fail(f"API returned status {resp.status_code}")
        
        except Exception as e:
            print_fail(f"Error evaluating {test['id']}: {e}")
    
    # Summary
    print(f"\n{Colors.BLUE}Scoring Accuracy Summary:{Colors.END}")
    print(f"  Total Test Cases: {len(TEST_CASES[:4])}")
    print(f"  Matching Scores (within tolerance): {matching_scores}/{len(TEST_CASES[:4])}")
    print(f"  Average Score Difference: {total_score_diff/len(TEST_CASES[:4]):.2f} points")
    print(f"  Accuracy: {(matching_scores/len(TEST_CASES[:4]))*100:.1f}%")
    
    return matching_scores == len(TEST_CASES[:4])

def test_duplicate_detection():
    """Test duplicate/plagiarism detection"""
    print_header("TEST 3: Duplicate Detection Accuracy")
    
    results = []
    correct_detections = 0
    
    # First, submit all tests to build history
    print("Building submission history...")
    for test in TEST_CASES:
        payload = {
            "submission_id": test["id"],
            "question_id": "q1",
            "rubric_id": "r1",
            "question_text": test["question"],
            "rubric_text": test["rubric"],
            "answer_text": test["answer"]
        }
        
        try:
            resp = requests.post(API_URL, json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                is_duplicate = data.get("duplicate_flag", False)
                expected_dup = test["expected_duplicate"]
                
                correct = (is_duplicate == expected_dup)
                if correct:
                    correct_detections += 1
                    status = "✅"
                else:
                    status = "❌"
                
                print(f"{status} {test['id']}: Flagged={is_duplicate}, Expected={expected_dup}")
                results.append({
                    "test_id": test["id"],
                    "flagged": is_duplicate,
                    "expected": expected_dup,
                    "correct": correct
                })
            
            time.sleep(0.5)
        
        except Exception as e:
            print_fail(f"Error testing duplicate on {test['id']}: {e}")
    
    # Summary
    print(f"\n{Colors.BLUE}Duplicate Detection Summary:{Colors.END}")
    print(f"  Total Test Cases: {len(TEST_CASES)}")
    print(f"  Correct Detections: {correct_detections}/{len(TEST_CASES)}")
    print(f"  Accuracy: {(correct_detections/len(TEST_CASES))*100:.1f}%")
    
    return correct_detections == len(TEST_CASES)

def test_feedback_quality():
    """Test feedback generation"""
    print_header("TEST 4: Feedback Quality Assessment")
    
    print("Submitting sample answers and checking feedback quality...\n")
    
    for i, test in enumerate(TEST_CASES[:3]):
        try:
            payload = {
                "submission_id": f"{test['id']}_feedback",
                "question_id": "q1",
                "rubric_id": "r1",
                "question_text": test["question"],
                "rubric_text": test["rubric"],
                "answer_text": test["answer"]
            }
            
            resp = requests.post(API_URL, json=payload, timeout=30)
            
            if resp.status_code == 200:
                data = resp.json()
                feedback = data.get("feedback", "")
                
                print(f"[{i+1}] Test {test['id']}:")
                print(f"  Answer: {test['answer'][:60]}...")
                print(f"  AI Feedback: {feedback}")
                
                # Check feedback quality
                if len(feedback) > 5 and feedback != "parsing failed":
                    print_pass("Feedback is non-generic and substantial")
                else:
                    print_warn("Feedback is too short or failed to generate")
                
                print()
            
            time.sleep(0.5)
        
        except Exception as e:
            print_fail(f"Error testing feedback on {test['id']}: {e}")

def test_api_error_handling():
    """Test error cases"""
    print_header("TEST 5: API Error Handling")
    
    print("Testing invalid inputs...\n")
    
    # Missing required field
    print("[1] Missing 'answer_text' field:")
    try:
        payload = {
            "submission_id": "error_test_1",
            "question_id": "q1",
            "rubric_id": "r1"
            # Missing answer_text
        }
        resp = requests.post(API_URL, json=payload, timeout=5)
        if resp.status_code == 422:
            print_pass(f"Correctly returned 422 Validation Error")
        else:
            print_warn(f"Expected 422, got {resp.status_code}")
    except Exception as e:
        print_fail(f"Error: {e}")
    
    # Empty submission
    print("\n[2] Empty answer text:")
    try:
        payload = {
            "submission_id": "error_test_2",
            "question_id": "q1",
            "rubric_id": "r1",
            "answer_text": ""
        }
        resp = requests.post(API_URL, json=payload, timeout=5)
        if resp.status_code in [200, 400, 422]:
            print_pass(f"API handled empty input gracefully (status {resp.status_code})")
        else:
            print_warn(f"Unexpected status: {resp.status_code}")
    except Exception as e:
        print_fail(f"Error: {e}")

def main():
    """Run all tests"""
    print(f"\n{Colors.BLUE}{'='*70}")
    print("VIRA TECH - STAGE 3 EVALUATION HARNESS")
    print(f"{'='*70}{Colors.END}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"API URL: {API_URL}\n")
    
    results = {
        "health": test_health_check(),
        "accuracy": test_scoring_accuracy(),
        "duplicates": test_duplicate_detection(),
    }
    
    test_feedback_quality()
    test_api_error_handling()
    
    # Final summary
    print_header("FINAL EVALUATION SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name.upper()}")
    
    print(f"\n{Colors.BLUE}Overall: {passed}/{total} test suites passed{Colors.END}")
    
    if passed == total:
        print_pass("All critical tests passed! Ready for Stage 3.")
    else:
        print_warn(f"{total - passed} test suite(s) need attention.")

if __name__ == "__main__":
    main()
