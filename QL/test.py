import pytest
import json
import os
import pandas as pd
from app import process_request

USER_ID = "8"
ITERATIONS = 1000  # Number of test cycles

# Define specific {persuasive_type, activity} combinations that get "Y"
ALLOWED_COMBINATIONS = {
    ("reminder", "meal planning"),
    ("suggestion", "meal planning"),
    ("reward", "meal planning"),
     ("praise", "meal planning"),
    # ("reminder", "water intake"),
    # ("suggestion", "water intake"),
    # ("reward", "water intake"),
    # ("praise", "water intake"),
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
 
USER_FILE_PATH = os.path.join(os.getcwd(), "documents", "userPath", f"{USER_ID}-user.csv")
MESSAGE_FILE_PATH = "documents\\messagePath\\message.csv"

def setup_files():
    """Setup test files before running tests."""
    os.makedirs("../documents/userPath", exist_ok=True)
    
    if not os.path.exists(MESSAGE_FILE_PATH):
        raise FileNotFoundError(f"Message file {MESSAGE_FILE_PATH} not found.")
    
    if os.path.exists(USER_FILE_PATH):
        os.remove(USER_FILE_PATH)



def test_qlearning_accuracy():
    setup_files()
    yes_count, no_count = 0, 0
    
    for _ in range(ITERATIONS):
        
        response = process_request({"invoke_type": 2, "userId": USER_ID})
        # Open user file and extract latest row
        file_path = os.path.join("documents", "userPath", f"{USER_ID}-user.csv")
        if os.path.exists(file_path):
            user_data = pd.read_csv(file_path)
            latest_row = user_data.iloc[-1]
            print("Latest entry in user file:")
        else:
            print("User file not found.")

        question_id = latest_row["id"]
        persuasive_type = latest_row["persuasive_type"].strip()
        activity = latest_row["activity"].strip()

        
        answer = (persuasive_type, activity) in ALLOWED_COMBINATIONS

        # # Answering the question
        answer_request = {
            "invoke_type": 3,
            "userId": USER_ID,
            "answer": answer,
            "questionId": question_id
            
        }
        response = process_request(answer_request)
      
        # Output the extracted values
        print(f"Question ID: {question_id}")
        print(f"Persuasive Type: {persuasive_type}")
        print(f"Activity: {activity}")
        print(f"Answer: {answer}")
        if answer:
            yes_count += 1
        else:
            no_count += 1

    accuracy = (yes_count / (yes_count + no_count)) * 100 if (yes_count + no_count) > 0 else 0
    assert accuracy >90  
if __name__ == "__main__":
    pytest.main(["-v","QL\\test.py"])
