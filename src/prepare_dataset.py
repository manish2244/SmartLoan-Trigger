import pandas as pd

# Original Kaggle dataset
input_file = "data/raw/bank.csv"

# Output file
output_file = "data/processed/smartloan_2500.csv"

# Read dataset
df = pd.read_csv(input_file)

# Take exactly 2500 records
df_2500 = df.sample(n=2500, random_state=42)

# Save the 2500-record dataset
df_2500.to_csv(output_file, index=False)

print("====================================")
print("SmartLoan Trigger Dataset Created")
print("====================================")
print("Original records :", len(df))
print("New records      :", len(df_2500))
print("Saved file       :", output_file)