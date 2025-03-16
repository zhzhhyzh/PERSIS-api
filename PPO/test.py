import pytest
import json
import pandas as pd
import os
from app import process_request

USER_ID = "4"
ITERATIONS = 1300  # Number of test cycles

# Define specific {persuasive_type, activity} combinations that get "Y"
ALLOWED_COMBINATIONS = {
    ("reminder", "meal planning"),
    ("suggestion", "meal planning"),
    ("reward", "meal planning"),
    ("praise", "meal planning"),
    ("reminder", "water intake"),
    ("suggestion", "water intake"),
    ("reward", "water intake"),
    ("praise", "water intake"),
    # ("reminder", "healthy eating"),
    # ("suggestion", "healthy eating"),
    # ("reward", "healthy eating"),
    # ("praise", "healthy eating"),
    # ("reminder", "portion control"),
    # ("suggestion", "portion control"),
    # ("reward", "portion control"),
    # ("praise", "portion control")
    
    
}

# File paths
USER_FILE_PATH = f"../documents/userPath/{USER_ID}-user.csv"
MESSAGE_FILE_PATH = "../documents/messagePath/message.csv"

def setup_files():
    """Setup test files before running tests."""
    if not os.path.exists("../documents/userPath"):
        os.makedirs("../documents/userPath")

    if not os.path.exists(MESSAGE_FILE_PATH):
        raise FileNotFoundError(f"Message file {MESSAGE_FILE_PATH} not found.")
    
    if os.path.exists(USER_FILE_PATH):
        os.remove(USER_FILE_PATH)

def test_ppo_accuracy():
    setup_files()
    yes_count = 0
    no_count = 0
    
    for _ in range(ITERATIONS):
        # Step 1: Request a new question
        request_data = {
            "invoke_type": 2,
            "userId": USER_ID
        }
        response = process_request(request_data)
        response_json = json.loads(response)
        
        if response_json["status"] != 200:
            continue  # Skip failed requests

        question_id = response_json["questionId"]
        persuasive_type = response_json["questionType"].strip()  # Remove spaces
        activity = response_json["activity"].strip()  # Remove spaces

        # Determine answer based on allowed combinations
        if (persuasive_type, activity) in ALLOWED_COMBINATIONS:
            answer = True
        else:
            answer = False

        # Debugging: Log unexpected "Y" responses
        if answer:
            print(f"✅ YES: ({persuasive_type}, {activity})")
        else:
            print(f"❌ NO: ({persuasive_type}, {activity})")

        # Step 2: Answer the question
        answer_request = {
            "invoke_type": 3,
            "userId": USER_ID,
            "questionId": question_id,
            "answer": answer
        }
        answer_response = process_request(answer_request)
        answer_json = json.loads(answer_response)
        
        if answer_json["status"] == 200:
            if answer:
                yes_count += 1
            else:
                no_count += 1

    accuracy = (yes_count / (yes_count + no_count)) * 100 if (yes_count + no_count) > 0 else 0
    print(f"Total Yes: {yes_count}, Total No: {no_count}, Accuracy: {accuracy:.2f}%")
    assert accuracy > 90  # Ensure at least 90% accuracy for "Y" responses.

if __name__ == "__main__":
    pytest.main(["-s", "test.py"])
