import pandas as pd
import os
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Define file paths
USER_DATA_PATH = "../documents/userPath/"
MESSAGE_DATA_PATH = "../documents/messagePath/message.csv"
EVAL_OUTPUT_PATH = "../documents/evaluation_data.csv"

# Load messages (Ground truth persuasive messages)
if not os.path.exists(MESSAGE_DATA_PATH):
    print("Message dataset not found.")
    exit()

messages_df = pd.read_csv(MESSAGE_DATA_PATH)

# Get all user response files
user_files = [f for f in os.listdir(USER_DATA_PATH) if f.endswith("-user.csv")]

# Initialize evaluation dataset
evaluation_data = []

# Process each user's data
for user_file in user_files:
    user_df = pd.read_csv(os.path.join(USER_DATA_PATH, user_file))

    for _, row in user_df.iterrows():
        if pd.isna(row["yesOrNo"]) or row["yesOrNo"] == "":
            continue  # Skip unanswered questions

        # Extract data
        actual_response = row["yesOrNo"].strip().upper()
        actual_type = row["persuasive_type"]
        actual_activity = row["activity"]

        # Find predicted persuasive message
        matched_message = messages_df[
            (messages_df["persuasive_type"] == actual_type) & 
            (messages_df["activity"] == actual_activity)
        ]

        is_correct_prediction = not matched_message.empty  # True if same persuasive_type & activity

        evaluation_data.append([
            row["id"], actual_response, actual_type, actual_activity, is_correct_prediction
        ])

# Save structured evaluation data
eval_df = pd.DataFrame(evaluation_data, columns=[
    "id", "actual_response", "actual_type", "actual_activity", "is_correct_prediction"
])

eval_df.to_csv(EVAL_OUTPUT_PATH, index=False)
print(f"Evaluation dataset saved: {EVAL_OUTPUT_PATH}")

# Load evaluation dataset
try:
    data = pd.read_csv(EVAL_OUTPUT_PATH)
    print(f"Loaded dataset with columns: {list(data.columns)}")
except FileNotFoundError:
    print("Evaluation dataset not found. Please check if user data exists.")
    exit()

# Ensure required columns exist
required_columns = ["actual_response", "is_correct_prediction"]
missing_columns = [col for col in required_columns if col not in data.columns]

if missing_columns:
    print(f"Missing columns in dataset: {missing_columns}")
    exit()

# Drop rows with missing values
data = data.dropna(subset=required_columns)

# Define binary labels
true_labels = data["is_correct_prediction"].astype(int)  # 1 if correct, 0 if incorrect
predicted_labels = (data["actual_response"] == "Y").astype(int)  # 1 if answered "Y", 0 otherwise

# Compute metrics
accuracy = accuracy_score(predicted_labels, true_labels)
precision = precision_score(true_labels, predicted_labels, zero_division=0)
recall = recall_score(true_labels, predicted_labels, zero_division=0)
f1 = f1_score(true_labels, predicted_labels, zero_division=0)

# Print results
print(f"Accuracy: {accuracy:.2f}")
print(f"Precision: {precision:.2f}")
print(f"Recall: {recall:.2f}")
print(f"F1-score: {f1:.2f}")
