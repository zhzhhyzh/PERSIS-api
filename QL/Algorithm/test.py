import pytest
import json
import pandas as pd
import os
import pickle
import random
from qlearning import get_next_message, update_q_table, initialize_q_table, save_q_table, load_q_table

USER_ID = "3"
ITERATIONS = 1300  # Number of test cycles

# Define specific {persuasive_type, activity} combinations that get "Y"
ALLOWED_COMBINATIONS = {
    #("reminder", "meal planning"),
    #("suggestion", "meal planning"),
    #("reward", "meal planning"),
    ("praise", "meal planning"),
    #("reminder", "water intake"),
    #("suggestion", "water intake"),
    ("reward", "water intake"),
    #("praise", "water intake"),
    ("reminder", "healthy eating"),
    #("suggestion", "healthy eating"),
    #("reward", "healthy eating"),
    ("praise", "healthy eating"),
    #("reminder", "portion control"),
    #("suggestion", "portion control"),
    #("reward", "portion control"),
    #("praise", "portion control")
}

# File paths
Q_TABLE_FILE = "q_table.pkl"

def setup_q_table():
    initialize_q_table() 

# def setup_q_table():
#     if not os.path.exists(Q_TABLE_FILE):
#         initialize_q_table()
#         save_q_table()
#     load_q_table()

def test_q_learning_accuracy():
    setup_q_table()
    yes_count = 0
    no_count = 0
    
    for _ in range(ITERATIONS):
        # Get the next message
        message, persuasive_type, activity = get_next_message()
        persuasive_type, activity = persuasive_type.strip(), activity.strip()
        

        # Determine response based on allowed combinations
        if (persuasive_type, activity) in ALLOWED_COMBINATIONS:
            response = 1  # Persuasive
        else:
            response = 0  # Not persuasive

        # Debugging logs
        if response:
            print(f"✅ YES: ({persuasive_type}, {activity})")
        else:
            print(f"❌ NO: ({persuasive_type}, {activity})")

        # Update Q-table
        update_q_table(message, persuasive_type, activity, response)
        
        if response:
            yes_count += 1
        else:
            no_count += 1
    #save_q_table()
    accuracy = (yes_count / (yes_count + no_count)) * 100 if (yes_count + no_count) > 0 else 0
    print(f"Total Yes: {yes_count}, Total No: {no_count}, Accuracy: {accuracy:.2f}%")
    assert accuracy > 90  # Ensure at least 90% accuracy for "Y" responses.

if __name__ == "__main__":
    pytest.main(["-v","-s", "test.py"])
