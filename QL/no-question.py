import sys
import json
import pandas as pd
import os
import datetime
import random
import pickle
import numpy as np

# Load API Input
def read_input():
    try:
        input_data = sys.stdin.read()
        return json.loads(input_data)
    except Exception as e:
        print(json.dumps({"status": 400, "message": f"Input parsing error: {str(e)}"}), file=sys.stderr)
        sys.exit(1)

# Return JSON Response
def return_json(status, message, question_id=None, persuasive_type=None, activity=None):
    def clean_value(value):
        """Convert NaN, inf, and other problematic values to safe JSON values"""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            if pd.isna(value) or np.isnan(value) or np.isinf(value):
                return None
            return value
        if isinstance(value, str) and (value.lower() == 'nan' or value == ''):
            return None
        return value
    
    response = {
        "status": clean_value(status),
        "message": clean_value(message),
        "questionId": clean_value(question_id),
        "persuasive_type": clean_value(persuasive_type),
        "activity": clean_value(activity)
    }
    print(json.dumps(response))
    sys.stdout.flush()
    return response


# Load Q-Table (Kept for structure, but no longer drives selection)
q_table = {}
epsilon = 0.5 

def load_q_table(user_id):
    file_path = os.path.join(os.getcwd(), "documents", "qlearning", f"{user_id}-q_table.pkl")
    global q_table
    if os.path.exists(file_path):
        try:
            with open(file_path, "rb") as f:
                loaded_table = pickle.load(f)
                # Clean any NaN values from loaded q_table
                q_table = {}
                for key, value in loaded_table.items():
                    if pd.isna(value) or np.isnan(value) or np.isinf(value):
                        q_table[key] = 0
                    else:
                        q_table[key] = value
        except Exception as e:
            print(f"Error loading Q-table: {str(e)}", file=sys.stderr)
            q_table = {}
    else:
        q_table = {}

def save_q_table(user_id):
    global q_table
    # Clean q_table before saving to remove any NaN values
    cleaned_q_table = {}
    for key, value in q_table.items():
        if pd.isna(value) or np.isnan(value) or np.isinf(value):
            cleaned_q_table[key] = 0
        else:
            cleaned_q_table[key] = value
    
    file_path = os.path.join(os.getcwd(), "documents", "qlearning", f"{user_id}-q_table.pkl")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        pickle.dump(cleaned_q_table, f)

# Initialize Q-Table (Kept for Q-table population)
def initialize_q_table(messages_df):
    global q_table
    for _, row in messages_df.iterrows():
        key = (row["message"], row["persuasive_type"], row["activity"])
        if key not in q_table:
            q_table[key] = 0  # Initialize Q-values to zero

# Get the next message using PURE RANDOMNESS (Replaces Q-learning logic)
def get_next_message_random():
    """
    Selects a message purely at random from the messages.csv dataset.
    This replaces the Q-learning exploration/exploitation logic.
    """
    try:
        # Load the master list of all available messages
        messages_df = pd.read_csv(os.path.join("documents", "messagePath", "message.csv"))
        
        if messages_df.empty:
            return None 

        # Use a purely random sampling
        selected_row = messages_df.sample(n=1).iloc[0]
        
        # Return the key components (message, persuasive_type, activity)
        selected_message = (
            str(selected_row['message']) if not pd.isna(selected_row['message']) else "",
            str(selected_row['persuasive_type']) if not pd.isna(selected_row['persuasive_type']) else "",
            str(selected_row['activity']) if not pd.isna(selected_row['activity']) else ""
        )
        
        return selected_message
        
    except Exception as e:
        print(f"Error in get_next_message_random: {str(e)}", file=sys.stderr)
        return None

# Update Q-Table based on user response (Q-learning formula remains, but selection is random)
def update_q_table(message, persuasive_type, activity, reward, question_id, learning_rate=0.001, gamma=0.99):
    key = (message, persuasive_type, activity)
    previous_value = q_table.get(key, 0)
    
    # Ensure previous_value is not NaN
    if pd.isna(previous_value) or np.isnan(previous_value) or np.isinf(previous_value):
        previous_value = 0
    
    # Reward shaping (increase reward if consistent positive feedback)
    if reward == 1:
        reward += 0.1
        if question_id == 1 or question_id == 2:
            # Simplified update for initial questions
            new_value = previous_value + learning_rate * (reward + gamma)
        else:
            # Q-Learning update (even though selection is random, we still track performance)
            max_q_value = 0
            if q_table:
                valid_values = [v for v in q_table.values() if not (pd.isna(v) or np.isnan(v) or np.isinf(v))]
                if valid_values:
                    max_q_value = max(valid_values)
            new_value = previous_value + learning_rate * (reward + gamma * max_q_value - previous_value)
    else:
        new_value = previous_value - 0.3
        if new_value < 0:
            new_value = 0
    
    # Ensure new_value is not NaN/inf
    if pd.isna(new_value) or np.isnan(new_value) or np.isinf(new_value):
        new_value = 0
    
    q_table[key] = new_value

# Load User Data
def load_user_data(user_id):
    file_path = os.path.join(os.getcwd(), "documents", "userPath", f"{user_id}-user.csv")

    # Check if the file exists
    if not os.path.exists(file_path):
        # Create an empty DataFrame with required columns
        empty_df = pd.DataFrame(columns=["id", "message", "persuasive_type", "activity", "yesOrNo", "Date", "Time"])
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Save the empty DataFrame as a new CSV file
        empty_df.to_csv(file_path, index=False)
        return empty_df

    # If file exists, load it with proper data types
    return pd.read_csv(file_path, dtype={"id": str, "message": str, "persuasive_type": str, "activity": str, "yesOrNo": str, "Date": str, "Time": str})


# Generate Question (invoke_type == 2)
def generate_question(user_id):
    try:
        load_q_table(user_id)
        user_data = load_user_data(user_id)
        messages_df = pd.read_csv(os.path.join("documents", "messagePath", "message.csv"))
        
        if messages_df is None or messages_df.empty:
            return return_json(400, "Message database is empty or missing.")

        if not user_data.empty:
            last_row = user_data.iloc[-1]
            last_question_id = last_row["id"]
            last_message = str(last_row["message"]) if not pd.isna(last_row["message"]) else ""
            last_type = str(last_row["persuasive_type"]) if not pd.isna(last_row["persuasive_type"]) else ""
            last_activity = str(last_row["activity"]) if not pd.isna(last_row["activity"]) else ""
            last_answer = str(last_row["yesOrNo"]) if not pd.isna(last_row["yesOrNo"]) else ""

            if last_answer == "" or last_answer.lower() == "nan":
                # Return the message as stored (already formatted)
                return return_json(200, last_message, last_question_id, last_type, last_activity)

        # Generate unique question ID
        question_id = len(user_data) + 1
        
        # Initialize selected_message to prevent NameError
        selected_message = None 
        
        if str(question_id) == "1":
            initialize_q_table(messages_df)
            # For first question, ensure variety by selecting from different types
            available_types = messages_df['persuasive_type'].unique()
            chosen_type = random.choice(available_types)
            type_messages = messages_df[messages_df['persuasive_type'] == chosen_type]
            selected_row = type_messages.sample(n=1).iloc[0]
            # FIX: Ensure selected_message is defined in this branch
            selected_message = (selected_row['message'], selected_row['persuasive_type'], selected_row['activity'])
            
        elif str(question_id) == "2":
            # For second question, pick a different type than the first one if possible
            if not user_data.empty:
                first_type = user_data.iloc[0]['persuasive_type']
                different_types = messages_df[messages_df['persuasive_type'] != first_type]
                if not different_types.empty:
                    selected_row = different_types.sample(n=1).iloc[0]
                    # FIX: Ensure selected_message is defined in this branch
                    selected_message = (selected_row['message'], selected_row['persuasive_type'], selected_row['activity'])
                else:
                    # Fallback to pure random if only one type exists
                    selected_message = get_next_message_random()
            else:
                # Should not happen if QID 1 logic ran, but safe fallback
                selected_message = get_next_message_random()
                
        else:
            # For QID 3+, use pure randomness (replaces Q-learning)
            selected_message = get_next_message_random()
            
        # Final check to ensure message was selected
        if selected_message is None or not all(selected_message):
            # Fallback if messages_df was empty or selection failed
            return return_json(500, "Failed to select a message after all attempts.")

        # Clean the selected message components to avoid NaN
        message_text = str(selected_message[0]) if not pd.isna(selected_message[0]) else ""
        persuasive_type = str(selected_message[1]) if not pd.isna(selected_message[1]) else ""
        activity = str(selected_message[2]) if not pd.isna(selected_message[2]) else ""

        # Create a formatted message that shows the persuasive strategy
        if message_text.startswith("🎯"):
            formatted_message = message_text
        else:
            persuasive_type_display = persuasive_type.title()
            activity_display = activity.title()
            formatted_message = f"🎯 {persuasive_type_display} Strategy for {activity_display}:\n\n{message_text}\n\n💡 This is a {persuasive_type} message to encourage {activity}."

        # Save question
        new_entry = pd.DataFrame([
            [question_id, formatted_message, persuasive_type, activity, "", "", ""]
        ], columns=["id", "message", "persuasive_type", "activity", "yesOrNo", "Date", "Time"])
        
        user_data = pd.concat([user_data, new_entry], ignore_index=True)
        output_dir = os.path.join("documents", "userPath")
        os.makedirs(output_dir, exist_ok=True)  

        file_path = os.path.join(os.getcwd(), "documents", "userPath", f"{user_id}-user.csv")
        user_data.to_csv(file_path, index=False)
        save_q_table(user_id) # Save Q-table with updated zero/non-zero values
        return return_json(200, formatted_message, question_id, persuasive_type, activity)
    except Exception as e:
        print(f"Error in generate_question: {str(e)}", file=sys.stderr)
        return return_json(500, f"Error generating question: {str(e)}")

# Answer Question (invoke_type == 3) - Remains mostly unchanged
def answer_question(user_id, question_id, answer):
    try:
        user_data = load_user_data(user_id)
        load_q_table(user_id)
        if question_id is None:
            return return_json(400, "Question ID is required")

        question_row = user_data[user_data["id"].astype(str) == str(question_id)]
        if question_row.empty:
            return return_json(400, "Failed: Question ID not found.")

        question_answered = question_row.iloc[0]["yesOrNo"]
        # Check if question is already answered (handle NaN values)
        if not pd.isna(question_answered) and str(question_answered) != "" and str(question_answered).lower() != "nan":
            return return_json(400, "Failed: Question ID already answered.")
            
        file_path = os.path.join(os.getcwd(), "documents", "userPath", f"{user_id}-user.csv")
        # Update answer
        gen_answer = "Y" if answer else "N"
        timestamp = datetime.datetime.now()
        user_data.loc[user_data["id"].astype(str) == str(question_id), ["yesOrNo", "Date", "Time"]] = [gen_answer, str(timestamp.date()), str(timestamp.time())]
        user_data.to_csv(file_path, index=False)

        # Update Q-table (Q-learning update logic is preserved for tracking purposes)
        question_data = question_row.iloc[0]
        reward = 1 if answer else 0
        
        # Clean question data to avoid NaN values
        message = str(question_data["message"]) if not pd.isna(question_data["message"]) else ""
        persuasive_type = str(question_data["persuasive_type"]) if not pd.isna(question_data["persuasive_type"]) else ""
        activity = str(question_data["activity"]) if not pd.isna(question_data["activity"]) else ""
        
        update_q_table(message, persuasive_type, activity, reward, int(question_id))
        save_q_table(user_id)

        return return_json(200, "Success")
    except Exception as e:
        print(f"Error in answer_question: {str(e)}", file=sys.stderr)
        return return_json(500, f"Error answering question: {str(e)}")

def process_request(request):
    try:
        invoke_type = request.get("invoke_type")
        user_id = request.get("username")
        answer = request.get("answer", "")
        question_id = request.get("questionId", None)

        if invoke_type == 2:
            return generate_question(user_id)
        elif invoke_type == 3:
            # Convert questionId to int for update_q_table logic
            try:
                if question_id is not None:
                    question_id = int(question_id)
            except ValueError:
                pass # Handled by the function if still string/None
            return answer_question(user_id, question_id, answer)
        else:
            return return_json(400, "Invalid invoke type")
    except Exception as e:
        print(f"Error in process_request: {str(e)}", file=sys.stderr)
        return return_json(500, f"Error processing request: {str(e)}")


# Main Execution
if __name__ == "__main__":
    try:
        request = read_input()
        process_request(request)
    except Exception as e:
        print(f"Main execution error: {str(e)}", file=sys.stderr)
        print(json.dumps({"status": 500, "message": f"Main execution error: {str(e)}"}))
        sys.exit(1)