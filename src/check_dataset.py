import pandas as pd

file_path = "data/raw/bank.csv"

df = pd.read_csv(file_path)

print("\n===== DATASET INFORMATION =====")
print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\n===== COLUMN NAMES =====")
print(df.columns.tolist())

print("\n===== FIRST 5 RECORDS =====")
print(df.head())

print("\n===== MISSING VALUES =====")
print(df.isnull().sum())