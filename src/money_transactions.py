import pandas as pd
import os

# =====================================================
# FILE PATHS
# =====================================================

INPUT_FILE = "data/processed/smartloan_2500.csv"
OUTPUT_FILE = "data/raw/money_transactions.csv"


# =====================================================
# LOAD EXISTING 2500 CUSTOMER DATA
# =====================================================

df = pd.read_csv(INPUT_FILE)

print("Existing customers:", len(df))

if len(df) != 2500:
    raise ValueError("smartloan_2500.csv must contain exactly 2500 customers.")


# =====================================================
# CREATE STABLE CUSTOMER IDs
# =====================================================

customer_ids = [
    f"C{i:05d}" for i in range(1, len(df) + 1)
]


# =====================================================
# CREATE SEPARATE MONEY DATASET
# =====================================================

money = pd.DataFrame()

money["customer_id"] = customer_ids


# =====================================================
# EXACT MONEY SEGMENTATION
# =====================================================
# 1 - 1100   = LOW MONEY
# 1101 - 1900 = MIDDLE MONEY
# 1901 - 2500 = HIGH MONEY

money["money_segment"] = "Low Money"

money.loc[1100:1899, "money_segment"] = "Middle Money"

money.loc[1900:2499, "money_segment"] = "High Money"


# =====================================================
# GENERATE SEGMENT-WISE MONTHLY INCOME
# =====================================================

money["monthly_income"] = 0.0

# LOW MONEY
low_mask = money["money_segment"] == "Low Money"

money.loc[low_mask, "monthly_income"] = (
    12000
    + df.loc[low_mask, "age"] * 100
    + df.loc[low_mask, "balance"].clip(lower=0) * 0.03
).round(0)


# MIDDLE MONEY
middle_mask = money["money_segment"] == "Middle Money"

money.loc[middle_mask, "monthly_income"] = (
    35000
    + df.loc[middle_mask, "age"] * 250
    + df.loc[middle_mask, "balance"].clip(lower=0) * 0.08
).round(0)


# HIGH MONEY
high_mask = money["money_segment"] == "High Money"

money.loc[high_mask, "monthly_income"] = (
    100000
    + df.loc[high_mask, "age"] * 700
    + df.loc[high_mask, "balance"].clip(lower=0) * 0.15
).round(0)


# =====================================================
# MONTHLY SPENDING
# =====================================================

money["monthly_spending"] = 0.0

money.loc[low_mask, "monthly_spending"] = (
    money.loc[low_mask, "monthly_income"] * 0.40
).round(0)

money.loc[middle_mask, "monthly_spending"] = (
    money.loc[middle_mask, "monthly_income"] * 0.50
).round(0)

money.loc[high_mask, "monthly_spending"] = (
    money.loc[high_mask, "monthly_income"] * 0.60
).round(0)


# =====================================================
# MONTHLY TRANSACTIONS
# =====================================================

money["monthly_transactions"] = (
    df["campaign"].clip(lower=1) * 3
    + df["previous"]
).astype(int)


# Give high-money customers higher transaction activity
money.loc[low_mask, "monthly_transactions"] = (
    money.loc[low_mask, "monthly_transactions"].clip(5, 20)
)

money.loc[middle_mask, "monthly_transactions"] = (
    money.loc[middle_mask, "monthly_transactions"].clip(15, 50)
)

money.loc[high_mask, "monthly_transactions"] = (
    money.loc[high_mask, "monthly_transactions"].clip(30, 100)
)


# =====================================================
# INVESTMENT AMOUNT
# =====================================================

money["investment_amount"] = 0.0

money.loc[low_mask, "investment_amount"] = (
    money.loc[low_mask, "monthly_income"] * 0.10
).round(0)

money.loc[middle_mask, "investment_amount"] = (
    money.loc[middle_mask, "monthly_income"] * 0.25
).round(0)

money.loc[high_mask, "investment_amount"] = (
    money.loc[high_mask, "monthly_income"] * 0.40
).round(0)


# =====================================================
# EMI AMOUNT
# =====================================================

money["emi_amount"] = (
    money["monthly_income"] * 0.15
).round(0)


# =====================================================
# SAVINGS AMOUNT
# =====================================================

money["savings_amount"] = (
    money["monthly_income"]
    - money["monthly_spending"]
    - money["emi_amount"]
).clip(lower=0).round(0)


# =====================================================
# DIGITAL PAYMENT COUNT
# =====================================================

money["digital_payment_count"] = (
    money["monthly_transactions"] * 0.70
).round(0).astype(int)


# =====================================================
# LOAN REPAYMENT STATUS
# =====================================================

money["loan_repayment_status"] = (
    df["loan"]
    .map({
        "yes": "Regular",
        "no": "No Active Loan"
    })
    .fillna("Regular")
)


# =====================================================
# SPENDING FREQUENCY
# =====================================================

money["spending_frequency"] = pd.cut(
    money["monthly_transactions"],
    bins=[-1, 10, 25, 1000],
    labels=["Low", "Medium", "High"]
)


# =====================================================
# FINANCIAL ACTIVITY SCORE
# =====================================================

money["financial_activity_score"] = (
    (
        money["monthly_spending"]
        / money["monthly_income"].replace(0, 1)
    ).clip(0, 1) * 30

    +

    (
        money["monthly_transactions"]
        / money["monthly_transactions"].max()
    ) * 25

    +

    (
        money["investment_amount"]
        / money["monthly_income"].replace(0, 1)
    ).clip(0, 1) * 20

    +

    (
        money["digital_payment_count"]
        / money["monthly_transactions"].replace(0, 1)
    ).clip(0, 1) * 25
)


money["financial_activity_score"] = (
    money["financial_activity_score"]
    .clip(0, 100)
    .round(2)
)


# =====================================================
# CREATE OUTPUT FOLDER
# =====================================================

os.makedirs("data/raw", exist_ok=True)


# =====================================================
# SAVE DATASET
# =====================================================

money.to_csv(
    OUTPUT_FILE,
    index=False
)


# =====================================================
# FINAL RESULTS
# =====================================================

print()
print("==========================================")
print("MONEY TRANSACTION DATASET CREATED")
print("==========================================")

print("Records:", len(money))
print("Columns:", len(money.columns))
print("Saved:", OUTPUT_FILE)

print()
print("==========================================")
print("MONEY SEGMENT DISTRIBUTION")
print("==========================================")

print(
    money["money_segment"].value_counts()
)


print()
print("==========================================")
print("SAMPLE DATA")
print("==========================================")

print(
    money[
        [
            "customer_id",
            "money_segment",
            "monthly_income",
            "monthly_spending",
            "investment_amount",
            "savings_amount",
            "monthly_transactions",
            "financial_activity_score"
        ]
    ].head(10).to_string(index=False)
)


print()
print("==========================================")
print("EXPECTED SEGMENTS")
print("==========================================")
print("Low Money    :", (money["money_segment"] == "Low Money").sum())
print("Middle Money :", (money["money_segment"] == "Middle Money").sum())
print("High Money   :", (money["money_segment"] == "High Money").sum())
print("Total        :", len(money))