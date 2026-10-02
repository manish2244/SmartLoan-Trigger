import pandas as pd
import joblib

# ==========================================
# Load trained model
# ==========================================

MODEL_FILE = "models/smartloan_model.pkl"
DATA_FILE = "data/processed/smartloan_features.csv"

model = joblib.load(MODEL_FILE)
df = pd.read_csv(DATA_FILE)

# ==========================================
# Select one customer
# ==========================================

customer = df.iloc[[0]].copy()

features = [
    "age",
    "job",
    "marital",
    "education",
    "default",
    "balance",
    "housing",
    "loan",
    "contact",
    "day",
    "month",
    "duration",
    "campaign",
    "pdays",
    "previous",
    "poutcome",
    "recently_contacted",
    "prev_success",
    "high_engagement",
    "healthy_balance",
    "right_time_score"
]

X_customer = customer[features]

# ==========================================
# Prediction
# ==========================================

prediction = model.predict(X_customer)[0]

probability = model.predict_proba(X_customer)[0][1]

# ==========================================
# Result
# ==========================================

print("========================================")
print("SMARTLOAN CUSTOMER PREDICTION")
print("========================================")

print("Customer ID:", 1)
print("Age:", customer["age"].iloc[0])
print("Job:", customer["job"].iloc[0])
print("Balance:", customer["balance"].iloc[0])

print("Right-Time Score:", customer["right_time_score"].iloc[0])
print("Recommended Action:", customer["recommended_action"].iloc[0])

print(
    "Prediction:",
    "Customer likely to accept offer"
    if prediction == 1
    else "Customer unlikely to accept offer"
)

print(f"Acceptance Probability: {probability * 100:.2f}%")