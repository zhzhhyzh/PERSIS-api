import pytest
import json
import os
import pandas as pd
from app import process_request

USER_ID = "3"
ITERATIONS = 1000  # Number of test cycles

# Define specific {persuasive_type, activity} combinations that get "Y"
ALLOWED_COMBINATIONS = {
    ("reminder", "meal planning"),
    ("suggestion", "meal planning"),
    ("reward", "meal planning"),
    # ("praise", "meal planning"),
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
USER_FILE_PATH = f"../documents/userPath/{USER_ID}-user.csv"
MESSAGE_FILE_PATH = "../documents/messagePath/message.csv"

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
        request_data = {"invoke_type": 2, "userId": USER_ID}
        response = process_request(request_data)

        # Debugging: Print response
        print("🛠️ Test Debug Response:", response)

        # Ensure response is not None
        assert response is not None, "❌ process_request() returned None"

        # Parse JSON safely
        try:
            response_data = json.loads(response)
        except json.JSONDecodeError:
            raise ValueError("❌ process_request() did not return valid JSON")

        # Check expected structure
        assert "status" in response_data, "❌ 'status' key missing in response"
        assert response_data["status"] == 200, "❌ Unexpected status in response"

if __name__ == "__main__":
    pytest.main(["-v", "test.py"])