import sys
import json
import pandas as pd
import random
import datetime
import os

# Read API input (JSON format)
def read_input():
    input_data = sys.stdin.read()
    return json.loads(input_data)

# Load or create user data
def get_user_data(user_id):
    user_file = f"{user_id}-user.csv"
    if os.path.exists(user_file):
        return pd.read_csv(user_file)
    else:
        return pd.DataFrame(columns=["id", "message", "persuasive_type", "yesOrNo", "Date", "Time"])

# Load or create profile data
def get_profile_data():
    profile_file = "profile.csv"
    if os.path.exists(profile_file):
        return pd.read_csv(profile_file)
    else:
        return pd.DataFrame(columns=["userId", "first_preference", "second_preference"])

# Save updated profile data
def save_profile_data(profile_data):
    profile_data.to_csv("profile.csv", index=False)

# Process API request
def process_request(request):
    invoke_type = request.get("invoke_type")
    user_id = request.get("userId")
    answer = request.get("answer", "")
    question_id = request.get("questionId", None)

    messages_df = pd.read_csv("message.csv")
    user_data = get_user_data(user_id)
    profile_data = get_profile_data()

    # CASE 1: Updating User Preferences
    if invoke_type == 1:
        if not isinstance(answer, list) or len(answer) != 2:
            return return_json(3, "Invalid preferences format. Please send two preferences.")

        # Update user preferences in profile.csv
        profile_data = profile_data[profile_data["userId"] != user_id]  # Remove old entry if exists
        new_profile = pd.DataFrame([[user_id, answer[0], answer[1]]], 
                                   columns=["userId", "first_preference", "second_preference"])
        profile_data = pd.concat([profile_data, new_profile], ignore_index=True)
        save_profile_data(profile_data)

        return return_json(3, "Success")

    # CASE 2: Question fetching
    elif invoke_type == 2:
        profile_row = profile_data[profile_data["userId"].astype(str) == str(user_id)]
        
        # Ask for preferences if they don't exist
        if profile_row.empty:
            return return_json(1, "Please enter two preferred message types.")

        first_preference = profile_row.iloc[0]["first_preference"]
        second_preference = profile_row.iloc[0]["second_preference"]

        # Occasionally explore a new message type (20% chance)
        explore = random.random() < 0.2
        if explore:
            explore_type = random.choice([t for t in messages_df["persuasive_type"].unique() if t not in [first_preference, second_preference]])
            second_preference = explore_type

        # Select a random message
        filtered_messages = messages_df[messages_df["persuasive_type"].isin([first_preference, second_preference])]
        if filtered_messages.empty:
            return return_json(3, "No messages available for your preferences.")

        random_message = filtered_messages.sample(n=1).iloc[0]
        question_id = len(user_data) + 1  # Unique question ID

        # Save the asked question in user data (without answer)
        new_entry = pd.DataFrame([[question_id, random_message["message"], random_message["persuasive_type"], "", "", ""]], 
                                 columns=["id", "message", "persuasive_type", "yesOrNo", "Date", "Time"])
        user_data = pd.concat([user_data, new_entry], ignore_index=True)
        user_data.to_csv(f"{user_id}-user.csv", index=False)

        return return_json(2, random_message["message"], question_id)

    # CASE 3: Update user answer in userId-user.csv
    elif invoke_type == 3:
        if question_id is None:
            return return_json(3, "Question ID is required")
        question_answering = user_data[user_data["id"].astype(str) == str(question_id)]
        question_answered = question_answering.iloc[0]["yesOrNo"]
        if pd.notna(question_answered) and question_answered != "":
            return return_json(3, "Failed: question ID already answered.")

        # Update the response
        gen_answer = "Y" if answer else "N"
        timestamp = datetime.datetime.now()
        user_data.loc[user_data["id"] == question_id, ["yesOrNo", "Date", "Time"]] = [gen_answer, timestamp.date(), timestamp.time()]
        user_data.to_csv(f"{user_id}-user.csv", index=False)

        return return_json(3, "Success")

    return return_json(3, "Invalid invoke_type")

# Function to format JSON response
def return_json(response_type, response, question_id=None):
    output = {
        "response_type": response_type,
        "response": response
    }
    if question_id is not None:
        output["questionId"] = question_id

    return json.dumps(output)

# Run the function
if __name__ == "__main__":
    request = read_input()
    response = process_request(request)
    # Unxpected Json Error
    if not response:
        response = json.dumps({"response_type": "error", "response": "No response from script"})
    
    print(response)
