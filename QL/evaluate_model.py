import os
import pickle
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Path Constants
BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), "documents"))
Q_TABLE_FILE = "q_table.pkl"
USER_DATA_PATH = os.path.join(BASE_DIR, "userPath") 
MESSAGE_DB_PATH = os.path.join(BASE_DIR, "messagePath", "message.csv") 

# Initialize Q-Table
q_table = {}

def load_q_table():
    """Loads the Q-table from a file or initializes it if not found."""
    global q_table
    if os.path.exists(Q_TABLE_FILE):
        with open(Q_TABLE_FILE, "rb") as f:
            q_table = pickle.load(f)
        print("Q-Table Loaded:", len(q_table), "entries")
    else:
        print("Q-table not found, initializing...")
        initialize_q_table()

def save_q_table():
    """Saves the Q-table to a file."""
    with open(Q_TABLE_FILE, "wb") as f:
        pickle.dump(q_table, f)
    print("Q-table saved.")

def initialize_q_table():
    """Creates the Q-table using data from the message database."""
    global q_table
    if not os.path.exists(MESSAGE_DB_PATH):
        print("Message database not found.")
        return
    
    messages_df = pd.read_csv(MESSAGE_DB_PATH)
    if messages_df.empty:
        print("Message database is empty.")
        return

    for _, row in messages_df.iterrows():
        key = (row["message"], row["persuasive_type"], row["activity"])
        if key not in q_table:
            q_table[key] = 0  # Initialize Q-values to zero
    
    save_q_table()

def load_evaluation_data(user_id="3"):
    """Loads user responses from a specific user file for evaluation."""
    user_file = os.path.join(USER_DATA_PATH, f"{user_id}-user.csv")

    if not os.path.exists(user_file):
        print(f"User file {user_id}-user.csv not found.")
        return None

    df = pd.read_csv(user_file)
    if "yesOrNo" in df.columns and "message" in df.columns:
        df = df.dropna(subset=["yesOrNo"])  # Remove unanswered questions
        df["actual"] = df["yesOrNo"].apply(lambda x: 1 if x.strip().upper() == "Y" else 0)
        df["predicted"] = df.apply(lambda row: 1 if (row["message"], row["persuasive_type"], row["activity"]) in q_table else 0, axis=1)

        return df

    print(f"User file {user_id}-user.csv does not have the required columns.")
    return None

def evaluate_model():
    """Evaluates the model using Accuracy, Recall, and Precision."""
    load_q_table()
    data = load_evaluation_data()
    
    if data is None or data.empty:
        print("No data available for evaluation.")
        return

    # Compute metrics
    accuracy = accuracy_score(data["actual"], data["predicted"])
    precision = precision_score(data["actual"], data["predicted"], zero_division=0)
    recall = recall_score(data["actual"], data["predicted"], zero_division=0)
    f1 = f1_score(data["actual"], data["predicted"], zero_division=0)

    print(f"QLearning Model Evaluation")
    print(f"Accuracy: {accuracy:.2f}")
    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")
    print(f"F1-score: {f1:.2f}")

# Run Evaluation
evaluate_model()
