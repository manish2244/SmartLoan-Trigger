import pandas as pd
import os

# =====================================================
# FILE PATHS
# =====================================================

CUSTOMER_FILE = "data/processed/smartloan_2500.csv"
MONEY_FILE = "data/raw/money_transactions.csv"

OUTPUT_FILE = "data/processed/smartloan_customer_profile.csv"


# =====================================================
# LOAD DATASETS
# =====================================================

customers = pd.read_csv(CUSTOMER_FILE)
money = pd.read_csv(MONEY_FILE)

print("==========================================")
print("DATASETS LOADED")
print("==========================================")
print("Customer records:", len(customers))
print("Money records   :", len(money))


# =====================================================
# VALIDATE DATA
# =====================================================

if len(customers) != 2500:
    raise ValueError("Customer dataset must contain exactly 2500 records.")

if len(money) != 2500:
    raise ValueError("Money dataset must contain exactly 2500 records.")


# =====================================================
# CREATE CUSTOMER ID
# =====================================================

customers["customer_id"] = [
    f"C{i:05d}" for i in range(1, len(customers) + 1)
]


# =====================================================
# MERGE CUSTOMER + FINANCIAL DATA
# =====================================================

df = customers.merge(
    money,
    on="customer_id",
    how="inner"
)


# =====================================================
# FINANCIAL POTENTIAL SCORE
# =====================================================

df["financial_potential_score"] = (
    df["financial_activity_score"] * 0.50
    +
    (
        df["right_time_score"]
        if "right_time_score" in df.columns
        else 0
    ) * 0.30
    +
    (
        (df["balance"].clip(lower=0) /
         df["balance"].clip(lower=0).max()) * 100
    ) * 0.20
)

df["financial_potential_score"] = (
    df["financial_potential_score"]
    .clip(0, 100)
    .round(2)
)


# =====================================================
# CUSTOMER CATEGORY
# =====================================================
# Use the exact money segment created in
# money_transactions.py.
#
# Low Money    = 1100
# Middle Money = 800
# High Money   = 600

if "money_segment" not in df.columns:
    raise ValueError(
        "money_segment column not found in money_transactions.csv"
    )

df["customer_category"] = df["money_segment"].map({
    "Low Money": "LOW",
    "Middle Money": "MEDIUM",
    "High Money": "HIGH"
})


# =====================================================
# CONTACT FREQUENCY
# =====================================================

def get_contact_frequency(category):

    if category == "HIGH":
        return "Every 7 Days"

    elif category == "MEDIUM":
        return "Every 30 Days"

    else:
        return "Every 60 Days"


df["contact_frequency"] = (
    df["customer_category"]
    .apply(get_contact_frequency)
)


# =====================================================
# NEXT CONTACT DAYS
# =====================================================

def get_next_contact_days(category):

    if category == "HIGH":
        return 7

    elif category == "MEDIUM":
        return 30

    else:
        return 60


df["next_contact_days"] = (
    df["customer_category"]
    .apply(get_next_contact_days)
)


# =====================================================
# RECOMMENDED ACTION
# =====================================================

def get_recommended_action(category):

    if category == "HIGH":
        return "Priority Offer / Call"

    elif category == "MEDIUM":
        return "SMS / Soft Reminder"

    else:
        return "Occasional Offer"


df["recommended_action"] = (
    df["customer_category"]
    .apply(get_recommended_action)
)


# =====================================================
# SAVE FINAL DATASET
# =====================================================

os.makedirs("data/processed", exist_ok=True)

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# =====================================================
# RESULTS
# =====================================================

print()
print("==========================================")
print("CUSTOMER SEGMENTATION COMPLETE")
print("==========================================")

print("Final records:", len(df))
print("Final columns:", len(df.columns))

print()
print("CUSTOMER CATEGORY")
print("------------------------------------------")

print(
    df["customer_category"]
    .value_counts()
)


print()
print("MONEY SEGMENT")
print("------------------------------------------")

print(
    df["money_segment"]
    .value_counts()
)


print()
print("CONTACT FREQUENCY")
print("------------------------------------------")

print(
    df["contact_frequency"]
    .value_counts()
)


print()
print("==========================================")
print("EXPECTED DISTRIBUTION")
print("==========================================")

print(
    "LOW / Low Money    :",
    (df["money_segment"] == "Low Money").sum()
)

print(
    "MEDIUM / Middle Money :",
    (df["money_segment"] == "Middle Money").sum()
)

print(
    "HIGH / High Money   :",
    (df["money_segment"] == "High Money").sum()
)


print()
print("Saved file:")
print(OUTPUT_FILE)


print()
print("Sample:")
print(
    df[
        [
            "customer_id",
            "money_segment",
            "balance",
            "monthly_income",
            "financial_activity_score",
            "financial_potential_score",
            "customer_category",
            "contact_frequency",
            "recommended_action"
        ]
    ].head(10).to_string(index=False)
)