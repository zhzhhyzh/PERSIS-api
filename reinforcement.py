import sys
import json
import pandas as pd
import os
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import datetime

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
    def __init__(self, state_size, action_size, hidden_size=128):
        self.model = MLP(state_size, hidden_size, action_size)
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.0005, weight_decay=1e-4)
        self.gamma = 0.96  # Discount factor
        self.epsilon = 0.15  # Clipping factor for PPO

    def select_action(self, state):
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        logits = self.model(state_tensor)

        # Ensure logits are finite
        if not torch.isfinite(logits).all():
            print("Warning: Logits contain NaN or Inf. Resetting to zeros.")
            logits = torch.zeros_like(logits)

        action_probs = torch.softmax(logits, dim=-1)

        # Prevent NaN probabilities
        if not torch.isfinite(action_probs).all():
            print("Warning: Action probabilities contain NaN. Resetting to uniform distribution.")
            action_probs = torch.ones_like(action_probs) / action_probs.shape[-1]

        try:
            action = torch.multinomial(action_probs, 1).item()
        except RuntimeError as e:
            print(f"Error in multinomial: {e}. Defaulting to random action.")
            action = np.random.randint(0, action_probs.shape[-1])  # Fallback action

        return action



    def update_policy(self, state, action, reward):
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        action_tensor = torch.tensor(action).unsqueeze(0)
        reward_tensor = torch.tensor(reward).float().unsqueeze(0)  # Ensure float

        logits = self.model(state_tensor)
        action_probs = torch.softmax(logits, dim=-1)

        # Debugging: Print logits and action probabilities
        print("Logits:", logits)
        print("Action Probabilities:", action_probs)

        # Ensure action probabilities are valid
        action_prob = torch.clamp(action_probs[0, action_tensor], min=1e-6, max=1.0)

        loss = -torch.log(action_prob) * reward_tensor

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()



# Initialize PPO agent
state_size = 2
action_size = 16  # Total possible combinations
ppo_agent = PPOAgent(state_size, action_size)

#calculate reward
def calculate_reward(answer):
    if answer == "Y":
        return np.random.uniform(3, 7)  # Random reward between 3–7
    elif answer == "N":
        return np.random.uniform(-2, -0.5)  # Random penalty between -2 and -0.5
    return -5  # Strong negative reward for missing an answer

# Read API input
def read_input():
    input_data = sys.stdin.read()
    return json.loads(input_data)

# Load user data
def get_user_data(user_id):
    user_file = f"./documents/userPath/{user_id}-user.csv"
    if os.path.exists(user_file):
        return pd.read_csv(user_file, dtype={"yesOrNo": str, "Date": str, "Time": str})
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

            if pd.isna(last_answer) or last_answer == "":
                return return_json(200, last_message, last_question_id, last_type, last_activity)

        last_type = "praise" if user_data.empty else last_row["persuasive_type"]
        last_activity = "water intake" if user_data.empty else last_row["activity"]

        state = [persuasive_types.index(last_type), activities.index(last_activity)]
        action = ppo_agent.select_action(state)
        selected_message = messages_df.iloc[action % len(messages_df)]
        question_id = len(user_data) + 1

        new_entry = pd.DataFrame([
            [question_id, selected_message["message"], selected_message["persuasive_type"], selected_message["activity"], "", "", ""]
        ], columns=["id", "message", "persuasive_type", "activity", "yesOrNo", "Date", "Time"])
        
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
        user_data.loc[user_data["id"] == question_id, ["yesOrNo", "Date", "Time"]] = [
            str(gen_answer),
            str(timestamp.date()),
            str(timestamp.time())
        ]
        
        user_data.to_csv(f"./documents/userPath/{user_id}-user.csv", index=False)
        
        last_row = user_data.iloc[-1]
        last_type = last_row["persuasive_type"]
        last_activity = last_row["activity"]
        state = [persuasive_types.index(last_type), activities.index(last_activity)]
        action = persuasive_types.index(last_type) * len(activities) + activities.index(last_activity)
        
        reward = calculate_reward(answer)
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

if __name__ == "__main__":
    request = read_input()
    response = process_request(request)
    if not response:
        response = json.dumps({"status": 500, "response": "No response from script"})
    print(response)
