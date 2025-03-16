import sys
import json
import pandas as pd
import os
import datetime
import random
import pickle

# Load API Input
def read_input():
    input_data = sys.stdin.read()
    return json.loads(input_data)

# Return JSON Response
def return_json(status, message, question_id=None, persuasive_type=None, activity=None):
    response = {
        "status": status,
        "message": message,
        "questionId": question_id,
        "persuasive_type": persuasive_type,
        "activity": activity
    }
    print(json.dumps(response))
    sys.stdout.flush()


# Load Q-Table
q_table = {}
epsilon = 0.5  # Initial exploration rate

def load_q_table():
    global q_table
    if os.path.exists("q_table.pkl"):
        with open("q_table.pkl", "rb") as f:
            q_table = pickle.load(f)

def save_q_table():
    with open("q_table.pkl", "wb") as f:
        pickle.dump(q_table, f)

# Initialize Q-Table
def initialize_q_table(messages_df):
    global q_table
    for _, row in messages_df.iterrows():
        key = (row["message"], row["persuasive_type"], row["activity"])
        if key not in q_table:
            q_table[key] = 0  # Initialize Q-values to zero

# Get the next message using Q-learning
def get_next_message(top_n_groups=4):
    global epsilon
    if random.random() < epsilon:  # Exploration: Randomly select a message
        message = random.choice(list(q_table.keys()))
    else:  # Exploitation: Choose from the top Q-value groups
        message_groups = {}
        for key, value in q_table.items():
            _, persuasive_type, activity = key
            if (persuasive_type, activity) not in message_groups:
                message_groups[(persuasive_type, activity)] = []
            message_groups[(persuasive_type, activity)].append((key, value))

        for group in message_groups.values():
            group.sort(key=lambda x: x[1], reverse=True)  # Sort messages in each group by Q-value

        sorted_groups = sorted(
            message_groups.items(),
            key=lambda item: max(item[1], key=lambda x: x[1])[1],
            reverse=True
        )

        selected_groups = sorted_groups[:top_n_groups]
        if selected_groups:
            chosen_group = random.choice(selected_groups)[1]
            message = random.choice(chosen_group)[0]
        else:
            message = random.choice(list(q_table.keys()))

    epsilon = max(0.01, epsilon * 0.99)  # Decrease exploration rate
    return message

# Update Q-Table based on user response
def update_q_table(message, persuasive_type, activity, reward, learning_rate=0.001, gamma=0.99):
    key = (message, persuasive_type, activity)
    previous_value = q_table.get(key, 0)
    if previous_value > 0 and reward == 1:
        reward += 0.2  # Encourage consistency
    q_table[key] = previous_value + learning_rate * (reward + gamma * max(q_table.values(), default=0) - previous_value)

# Load User Data
def load_user_data(user_id):
    BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), "documents"))
    file_path = os.path.join(BASE_DIR, "userPath", f"{user_id}-user.csv")  
    if not os.path.exists(file_path):
        print("998/n")
        return pd.DataFrame(columns=["id", "message", "persuasive_type", "activity", "yesOrNo", "Date", "Time"])
    return pd.read_csv(file_path)

# Generate Question (invoke_type == 2)
def generate_question(user_id):
    user_data = load_user_data(user_id)
    BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), "documents"))
    messages_df = pd.read_csv(os.path.join(BASE_DIR, "messagePath", "message.csv"))
    
    if messages_df is None or messages_df.empty:
        return return_json(400, "Message database is empty or missing.")

    load_q_table()
    initialize_q_table(messages_df)

    selected_message = get_next_message()

    # Generate unique question ID
    question_id = len(user_data) + 1

    # Save question
    new_entry = pd.DataFrame([
        [question_id, selected_message[0], selected_message[1], selected_message[2], "", "", ""]
    ], columns=["id", "message", "persuasive_type", "activity", "yesOrNo", "Date", "Time"])
    
    user_data = pd.concat([user_data, new_entry], ignore_index=True)
    output_dir = os.path.join(BASE_DIR, "userPath")
    os.makedirs(output_dir, exist_ok=True)  
    file_path = os.path.join(output_dir, f"{user_id}-user.csv")
    user_data.to_csv(file_path, index=False)

    return_json(200, selected_message[0], question_id, selected_message[1], selected_message[2])

# Answer Question (invoke_type == 3)
def answer_question(user_id, question_id, answer):
    user_data = load_user_data(user_id)

    if question_id is None:
        return return_json(400, "Question ID is required")

    question_row = user_data[user_data["id"].astype(str) == str(question_id)]
    if question_row.empty:
        return return_json(400, "Failed: Question ID not found.")

    question_answered = question_row.iloc[0]["yesOrNo"]
    if pd.notna(question_answered) and question_answered != "":
        return return_json(400, "Failed: Question ID already answered.")

    # Update answer
    gen_answer = "Y" if answer else "N"
    timestamp = datetime.datetime.now()
    user_data.loc[user_data["id"] == question_id, ["yesOrNo", "Date", "Time"]] = [gen_answer, str(timestamp.date()), str(timestamp.time())]
    BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), "documents"))
    user_data.to_csv(os.path.join(BASE_DIR, "userPath", f"{user_id}-user.csv") ,index=False)

    # Update Q-table
    load_q_table()
    question_data = question_row.iloc[0]
    reward = 1 if answer else -1
    update_q_table(question_data["message"], question_data["persuasive_type"], question_data["activity"], reward)
    save_q_table()

    return return_json(200, "Success")

def process_request(request):
    invoke_type = request.get("invoke_type")
    user_id = request.get("userId")
    answer = request.get("answer", "")
    question_id = request.get("questionId", None)

    if invoke_type == 2:
        return generate_question(user_id)  # Return instead of printing
    elif invoke_type == 3:
        return answer_question(user_id, question_id, answer)
    else:
        return return_json(400, "Invalid invoke type")

# Main Execution
if __name__ == "__main__":
    request = read_input()
    process_request(request)
    
