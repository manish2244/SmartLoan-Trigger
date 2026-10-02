import pandas as pd

INPUT_FILE = "data/processed/smartloan_2500.csv"
OUTPUT_FILE = "data/processed/smartloan_features.csv"

# Load dataset
df = pd.read_csv(INPUT_FILE)

# -------------------------------------------------
# 1. Recently Contacted
# -------------------------------------------------
# pdays <= 30 means customer was contacted recently
df["recently_contacted"] = (df["pdays"].between(0, 30)).astype(int)

# -------------------------------------------------
# 2. Previous Success
# -------------------------------------------------
# Previous campaign outcome was successful
df["prev_success"] = (df["poutcome"] == "success").astype(int)

# -------------------------------------------------
# 3. High Engagement
# -------------------------------------------------
# Long call duration indicates higher engagement
duration_threshold = df["duration"].median()
df["high_engagement"] = (
    df["duration"] >= duration_threshold
).astype(int)

# -------------------------------------------------
# 4. Healthy Balance
# -------------------------------------------------
# Positive balance indicates available funds
df["healthy_balance"] = (df["balance"] > 0).astype(int)

# -------------------------------------------------
# 5. Right-Time Score
# -------------------------------------------------
# Four signals, each contributing 25 points
df["right_time_score"] = (
    df["recently_contacted"] * 25
    + df["prev_success"] * 25
    + df["high_engagement"] * 25
    + df["healthy_balance"] * 25
)

# -------------------------------------------------
# 6. Recommended Action
# -------------------------------------------------
def get_action(score):
    if score >= 75:
        return "Contact Now"
    elif score >= 50:
        return "Soft Reminder"
    else:
        return "Re-check in 60 days"

df["recommended_action"] = df["right_time_score"].apply(get_action)

# Save processed dataset
df.to_csv(OUTPUT_FILE, index=False)

# -------------------------------------------------
# Results
# -------------------------------------------------
print("========================================")
print("SmartLoan Feature Engineering Complete")
print("========================================")
print("Records:", len(df))
print("Columns:", len(df.columns))
print()
print("New Features:")
print("- recently_contacted")
print("- prev_success")
print("- high_engagement")
print("- healthy_balance")
print("- right_time_score")
print("- recommended_action")
print()
print("Score Distribution:")
print(df["right_time_score"].value_counts().sort_index())
print()
print("Action Distribution:")
print(df["recommended_action"].value_counts())
print()
print("Saved:", OUTPUT_FILE)