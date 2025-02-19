import sys
import json
import pandas as pd
import random
import datetime
import os
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

# Define the MLP model (neural network)
class MLP(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(MLP, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# Define PPO agent
class PPOAgent:
    def __init__(self, state_size, action_size, hidden_size=64):
        self.model = MLP(state_size, hidden_size, action_size)
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.gamma = 0.99  # Discount factor
        self.epsilon = 0.2  # Clipping factor for PPO

    def select_action(self, state):
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        logits = self.model(state_tensor)
        action_probs = torch.softmax(logits, dim=-1)
        action = torch.multinomial(action_probs, 1).item()
        return action

    def update_policy(self, state, action, reward):
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        action_tensor = torch.tensor(action).unsqueeze(0)
        reward_tensor = torch.tensor(reward).unsqueeze(0)

        logits = self.model(state_tensor)
        action_probs = torch.softmax(logits, dim=-1)
        action_prob = action_probs[0, action_tensor]
        loss = -torch.log(action_prob) * reward_tensor

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

# Initialize PPO agent
state_size = 2  # Two features: persuasive_type and activity
action_size = 16  # Two possible actions (question selections)
ppo_agent = PPOAgent(state_size, action_size)

# Read API input
def read_input():
    input_data = sys.stdin.read()
    return json.loads(input_data)

# Load user data
def get_user_data(user_id):
    user_file = f"./documents/userPath/{user_id}-user.csv"
    if os.path.exists(user_file):
        return pd.read_csv(user_file)
    else:
        return pd.DataFrame(columns=["id", "message", "persuasive_type", "activity", "yesOrNo", "Date", "Time"])

# Process request
def process_request(request):
    invoke_type = request.get("invoke_type")
    user_id = request.get("userId")
    answer = request.get("answer", "")
    question_id = request.get("questionId", None)

    messages_df = pd.read_csv("./documents/messagePath/message.csv")
    user_data = get_user_data(user_id)

    persuasive_types = ["praise", "reminder", "suggestion", "reward"]
    activities = ["water intake", "portion control", "healthy eating", "meal planning"]

    if invoke_type == 2:
        if not user_data.empty:
            last_row = user_data.iloc[-1]
            last_question_id = last_row["id"]
            last_message = last_row["message"]
            last_type = last_row["persuasive_type"]
            last_activity = last_row["activity"]
            last_answer = last_row["yesOrNo"]

            # If the last question is unanswered, return it
            if pd.isna(last_answer) or last_answer == "":
                return return_json(200, last_message, last_question_id, last_type, last_activity)

        # If last question was answered, proceed with selecting a new question
        last_type = "praise" if user_data.empty else last_row["persuasive_type"]
        last_activity = "water intake" if user_data.empty else last_row["activity"]

        state = [persuasive_types.index(last_type), activities.index(last_activity)]
        action = ppo_agent.select_action(state)

        selected_message = messages_df.iloc[action % len(messages_df)]
        question_id = len(user_data) + 1

        new_entry = pd.DataFrame(
            [[question_id, selected_message["message"], selected_message["persuasive_type"], selected_message["activity"], "", "", ""]],
            columns=["id", "message", "persuasive_type", "activity", "yesOrNo", "Date", "Time"]
        )
        user_data = pd.concat([user_data, new_entry], ignore_index=True)
        user_data.to_csv(f"./documents/userPath/{user_id}-user.csv", index=False)

        return return_json(200, selected_message["message"], question_id, selected_message["persuasive_type"], selected_message["activity"])

    elif invoke_type == 3:
        if question_id is None:
            return return_json(400, "Question ID is required")
        
        question_answering = user_data[user_data["id"].astype(str) == str(question_id)]
        if question_answering.empty:
            return return_json(400, "Failed: Question ID not found.")
        
        question_answered = question_answering.iloc[0]["yesOrNo"]
        if pd.notna(question_answered) and question_answered != "":
            return return_json(400, "Failed: question ID already answered.")
        
        gen_answer = "Y" if answer else "N"
        timestamp = datetime.datetime.now()
        user_data.loc[user_data["id"] == question_id, ["yesOrNo", "Date", "Time"]] = [gen_answer, timestamp.date(), timestamp.time()]
        user_data.to_csv(f"./documents/userPath/{user_id}-user.csv", index=False)
        
        # Get last known state for updating policy
        last_row = user_data.iloc[-1]
        last_type = last_row["persuasive_type"]
        last_activity = last_row["activity"]
        state = [persuasive_types.index(last_type), activities.index(last_activity)]
        action = persuasive_types.index(last_type) * len(activities) + activities.index(last_activity)
        
        reward = 1 if answer == "Y" else -1
        ppo_agent.update_policy(state, action, reward)

        return return_json(200, "Success")
    
    return return_json(400, "Invalid invoke_type")

# Format JSON response
def return_json(status, response, question_id=None, question_type=None, activity=None):
    output = {"status": status, "response": response}
    if question_id is not None:
        output["questionId"] = question_id
        output["questionType"] = question_type
        output["activity"] = activity
    return json.dumps(output)

# Run the function
if __name__ == "__main__":
    request = read_input()
    response = process_request(request)
    if not response:
        response = json.dumps({"status": 500, "response": "No response from script"})
    print(response)
