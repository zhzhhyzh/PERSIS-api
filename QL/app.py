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


# Load Q-Table
q_table = {}
epsilon = 0.5  # Initial exploration rate

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


# Capture Q-value convergence data
def capture_convergence_data(user_id, response_type=None, question_data=None):
    """
    Log convergence data in simple text format.
    
    Args:
        user_id (str): The username
        response_type (str): "OK" or "Cancel" 
        question_data (dict): Question details including message, persuasive_type, activity
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if question_data is not None:
        # Extract question details
        message = str(question_data.get("message", ""))
        persuasive_type = question_data.get("persuasive_type", "")
        activity = question_data.get("activity", "")
        
        # Truncate message if too long for logging
        truncated_message = message[:100] + "..." if len(message) > 100 else message
        # Remove newlines and extra spaces for clean logging, and handle encoding
        clean_message = truncated_message.replace('\n', ' ').replace('\r', ' ').strip()
        # Remove emojis and special characters that might cause encoding issues
        import re
        clean_message = re.sub(r'[^\x00-\x7F]+', '', clean_message)
        
        # Get Q-value for this specific question
        q_value = q_table.get((str(question_data.get("message", "")), persuasive_type, activity), 0)
        
        log_entry = f"[{timestamp}] [{user_id}] [{response_type}] [{persuasive_type}] [{activity}] [{clean_message}] [{q_value:.6f}]\n"
    else:
        # Fallback for general convergence logging
        q_values = list(q_table.values())
        avg_q = sum(q_values) / len(q_values) if q_values else 0
        log_entry = f"[{timestamp}] [{user_id}] [SYSTEM] [Convergence Check] [{avg_q:.6f}]\n"
    
    # Log file path
    log_file_path = os.path.join(os.getcwd(), "documents", "qlearning", "convergence.log")
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    
    # Append to log file
    with open(log_file_path, "a") as f:
        f.write(log_entry)

# Log user interaction to text file
def log_user_interaction(user_id, response_type, q_value, question_type=None, question_text=None):
    """
    Log user interaction to a text file.
    
    Args:
        user_id (str): The username
        response_type (str): "OK" or "Cancel"
        q_value (float): The current Q-value for the answered question
        question_type (str): The type of the question (optional)
        question_text (str): The text of the question (optional)
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_entry = f"{timestamp} | User: {user_id} | Response: {response_type} | Q-Value: {q_value:.6f}"
    if question_type:
        log_entry += f" | Question Type: {question_type}"
    if question_text:
        # Clean the question text to remove emojis and special characters
        import re
        clean_text = re.sub(r'[^\x00-\x7F]+', '', question_text)
        # Truncate long question text for readability
        truncated_text = clean_text[:50] + "..." if len(clean_text) > 50 else clean_text
        log_entry += f" | Question: {truncated_text}"
    log_entry += "\n"
    
    # Log file path
    log_file_path = os.path.join(os.getcwd(), "documents", "qlearning", "user_interactions.log")
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    
    # Append to log file
    with open(log_file_path, "a") as f:
        f.write(log_entry)
        
# Initialize Q-Table
def initialize_q_table(messages_df):
    global q_table
    for _, row in messages_df.iterrows():
        key = (row["message"], row["persuasive_type"], row["activity"])
        if key not in q_table:
            q_table[key] = 0  # Initialize Q-values to zero

# Get the next message using Q-learning
def get_next_message():
    global epsilon
    global q_table
    num = random.random()
    
    # Increase exploration to get more variety - use 50% exploration for better variety
    if num < max(0.5, epsilon):  # Minimum 50% exploration for variety
        message = random.choice(list(q_table.keys()))
        
    else:  # Exploitation: Choose from the top Q-value groups with better variety
        # Step 1: Group messages by (persuasive_type, activity) and store max Q-value per group
        message_groups = {}
        for key, value in q_table.items():
            _, persuasive_type, activity = key
            if (persuasive_type, activity) not in message_groups:
                message_groups[(persuasive_type, activity)] = []
            message_groups[(persuasive_type, activity)].append((key, value))

        # Step 2: Sort each group by Q-value (descending)
        for group in message_groups.values():
            group.sort(key=lambda x: x[1], reverse=True)  # Sort messages in each group by Q-value

        # Step 3: Get groups with different persuasive types to ensure variety
        type_variety = {}
        for (persuasive_type, activity), messages in message_groups.items():
            if persuasive_type not in type_variety:
                type_variety[persuasive_type] = []
            type_variety[persuasive_type].append(((persuasive_type, activity), messages))
        
        # Step 4: Choose from different persuasive types for variety
        if len(type_variety) > 1:
            # Randomly pick a persuasive type we haven't used recently
            chosen_type = random.choice(list(type_variety.keys()))
            chosen_group_data = random.choice(type_variety[chosen_type])
            chosen_group = chosen_group_data[1]
            message = random.choice(chosen_group)[0]  # Pick a random message from that group
        else:
            # Fallback to original logic if only one type available
            sorted_groups = sorted(
                message_groups.items(),
                key=lambda item: max(item[1], key=lambda x: x[1])[1],  # Get the max Q-value from each group
                reverse=True
            )
            
            if sorted_groups:
                chosen_group = random.choice(sorted_groups[:5])[1] if len(sorted_groups) >= 5 else random.choice(sorted_groups)[1]  # Pick from top 5 groups for more variety
                message = random.choice(chosen_group)[0]  # Pick a random message from that group
            else:
                message = random.choice(list(q_table.keys()))  # Fallback random choice

    epsilon = max(0.1, epsilon * 0.98)  # Slower decay to maintain more exploration, minimum 10%
    return message

# Update Q-Table based on user response
def update_q_table(message, persuasive_type, activity, reward, question_id, learning_rate=0.001, gamma=0.99):
    key = (message, persuasive_type, activity)
    previous_value = q_table.get(key, 0)
    
    # Ensure previous_value is not NaN
    if pd.isna(previous_value) or np.isnan(previous_value) or np.isinf(previous_value):
        previous_value = 0
    
    # Reward shaping (increase reward if consistent positive feedback)
    if reward == 1:
        reward += 0.1  # Reduce bonus to avoid over-optimization of single type
        if question_id == 1 or question_id == 2:
            new_value = previous_value + learning_rate * (reward + gamma)
        else:
            # Safely calculate max value, handling potential NaN/inf values
            max_q_value = 0
            if q_table:
                valid_values = [v for v in q_table.values() if not (pd.isna(v) or np.isnan(v) or np.isinf(v))]
                if valid_values:
                    max_q_value = max(valid_values)
            new_value = previous_value + learning_rate * (reward + gamma * max_q_value - previous_value)
    else:
        new_value = previous_value - 0.3  # Reduce penalty to avoid eliminating types too quickly
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
        global q_table
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
        if str(question_id) == "1":
            initialize_q_table(messages_df)
            # For first question, ensure variety by selecting from different types
            available_types = messages_df['persuasive_type'].unique()
            chosen_type = random.choice(available_types)
            type_messages = messages_df[messages_df['persuasive_type'] == chosen_type]
            selected_row = type_messages.sample(n=1).iloc[0]
            selected_message = (selected_row['message'], selected_row['persuasive_type'], selected_row['activity'])
        elif str(question_id) == "2":
            # For second question, pick a different type than the first one if possible
            if not user_data.empty:
                first_type = user_data.iloc[0]['persuasive_type']
                different_types = messages_df[messages_df['persuasive_type'] != first_type]
                if not different_types.empty:
                    selected_row = different_types.sample(n=1).iloc[0]
                    selected_message = (selected_row['message'], selected_row['persuasive_type'], selected_row['activity'])
                else:
                    selected_message = random.choice(list(q_table.keys()))
            else:
                selected_message = random.choice(list(q_table.keys()))
        else:
            selected_message = get_next_message()        # Clean the selected message components to avoid NaN
        message_text = str(selected_message[0]) if not pd.isna(selected_message[0]) else ""
        persuasive_type = str(selected_message[1]) if not pd.isna(selected_message[1]) else ""
        activity = str(selected_message[2]) if not pd.isna(selected_message[2]) else ""

        # Create a formatted message that shows the persuasive strategy
        # Only format if it's not already formatted
        if message_text.startswith("🎯"):
            formatted_message = message_text  # Already formatted
        else:
            persuasive_type_display = persuasive_type.title()  # Capitalize first letter
            activity_display = activity.title()  # Capitalize first letter
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
        save_q_table(user_id)
        return return_json(200, formatted_message, question_id, persuasive_type, activity)
    except Exception as e:
        print(f"Error in generate_question: {str(e)}", file=sys.stderr)
        return return_json(500, f"Error generating question: {str(e)}")

# Answer Question (invoke_type == 3)
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

        # Update Q-table
        question_data = question_row.iloc[0]
        reward = 1 if answer else 0
        
        # Clean question data to avoid NaN values
        message = str(question_data["message"]) if not pd.isna(question_data["message"]) else ""
        persuasive_type = str(question_data["persuasive_type"]) if not pd.isna(question_data["persuasive_type"]) else ""
        activity = str(question_data["activity"]) if not pd.isna(question_data["activity"]) else ""
        
        update_q_table(message, persuasive_type, activity, reward, question_id)
        save_q_table(user_id)

        # Log user interaction
        q_value = q_table.get((message, persuasive_type, activity), 0)
        response_type = "OK" if answer else "Cancel"
        log_user_interaction(user_id, response_type, q_value, persuasive_type, message)

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
