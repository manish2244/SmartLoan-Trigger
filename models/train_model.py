# =========================================================
# SMARTLOAN TRIGGER — MODEL TRAINING SCRIPT
# Training: 80% | Testing: 20%
# =========================================================

import pandas as pd
import numpy as np
import joblib
import os
import sys
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

FEATURES_FILE = os.path.join(
    PROJECT_ROOT, "data", "processed", "smartloan_features.csv"
)

MODEL_FILE = os.path.join(
    PROJECT_ROOT, "models", "smartloan_model.pkl"
)

REPORT_DIR = os.path.join(PROJECT_ROOT, "reports")

# =========================================================
# HEADER
# =========================================================

print("=" * 60)
print(" SMARTLOAN TRIGGER — MODEL TRAINING")
print("=" * 60)

# =========================================================
# LOAD DATA
# =========================================================

print("\n📂 Loading dataset...")

if not os.path.exists(FEATURES_FILE):
    print(f"❌ Dataset not found: {FEATURES_FILE}")
    sys.exit(1)

df = pd.read_csv(FEATURES_FILE)

print(f"✅ Dataset loaded: {df.shape[0]} rows × {df.shape[1]} columns")

# =========================================================
# CHECK TARGET COLUMN
# =========================================================

TARGET = "deposit"

if TARGET not in df.columns:
    print(f"❌ Target column '{TARGET}' not found!")
    print(f"Available columns: {list(df.columns)}")
    sys.exit(1)

# =========================================================
# ENCODE CATEGORICAL COLUMNS
# =========================================================

print("\n🔧 Encoding categorical features...")

df_encoded = df.copy()

categorical_cols = df_encoded.select_dtypes(include=["object"]).columns.tolist()
categorical_cols = [c for c in categorical_cols if c != TARGET]

# Target ko 0/1 me convert karo
if df_encoded[TARGET].dtype == "object":
    df_encoded[TARGET] = df_encoded[TARGET].map({
        "yes": 1, "no": 0, "Yes": 1, "No": 0, "YES": 1, "NO": 0
    })

df_encoded = df_encoded.dropna(subset=[TARGET])

# Baaki categorical columns ko encode karo
for col in categorical_cols:
    df_encoded[col] = df_encoded[col].astype("category").cat.codes

print(f"✅ Encoded {len(categorical_cols)} categorical columns")

# =========================================================
# FEATURES & TARGET
# =========================================================

FEATURES = [
    "age", "job", "marital", "education", "default",
    "balance", "housing", "loan", "contact",
    "day", "month", "duration", "campaign",
    "pdays", "previous", "poutcome",
    "recently_contacted", "prev_success",
    "high_engagement", "healthy_balance",
    "right_time_score"
]

available_features = [f for f in FEATURES if f in df_encoded.columns]

print(f"\n📊 Using {len(available_features)} features for training")

X = df_encoded[available_features]
y = df_encoded[TARGET].astype(int)

# =========================================================
# TRAIN-TEST SPLIT (80-20)
# =========================================================

print("\n🔀 Splitting data (80% train / 20% test)...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print(f"   ✅ Training set: {X_train.shape[0]} samples (80%)")
print(f"   ✅ Testing set:  {X_test.shape[0]} samples (20%)")

# =========================================================
# TRAIN MODEL
# =========================================================

print("\n🤖 Training Random Forest model...")

model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

print("✅ Model trained successfully!")

# =========================================================
# EVALUATE
# =========================================================

print("\n📈 Evaluating model on test set...")

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, zero_division=0)
recall = recall_score(y_test, y_pred, zero_division=0)
f1 = f1_score(y_test, y_pred, zero_division=0)

print("\n" + "=" * 60)
print(" MODEL PERFORMANCE")
print("=" * 60)
print(f"   Accuracy:  {accuracy * 100:.2f}%")
print(f"   Precision: {precision * 100:.2f}%")
print(f"   Recall:    {recall * 100:.2f}%")
print(f"   F1 Score:  {f1 * 100:.2f}%")
print("=" * 60)

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
print("\n📊 Confusion Matrix:")
print(f"   True Negatives:  {cm[0][0]}")
print(f"   False Positives: {cm[0][1]}")
print(f"   False Negatives: {cm[1][0]}")
print(f"   True Positives:  {cm[1][1]}")

# Classification Report
print("\n📋 Classification Report:")
print(classification_report(y_test, y_pred, zero_division=0))

# =========================================================
# SAVE MODEL
# =========================================================

print(f"\n💾 Saving model to: {MODEL_FILE}")
joblib.dump(model, MODEL_FILE)
print("✅ Model saved successfully!")

# =========================================================
# SAVE REPORT
# =========================================================

os.makedirs(REPORT_DIR, exist_ok=True)
report_file = os.path.join(REPORT_DIR, "model_report.txt")

with open(report_file, "w", encoding="utf-8") as f:
    f.write("=" * 60 + "\n")
    f.write(" SMARTLOAN TRIGGER — MODEL TRAINING REPORT\n")
    f.write("=" * 60 + "\n\n")
    f.write(f"Dataset Size:       {df.shape[0]} rows\n")
    f.write(f"Training Samples:   {X_train.shape[0]} (80%)\n")
    f.write(f"Testing Samples:    {X_test.shape[0]} (20%)\n")
    f.write(f"Features Used:      {len(available_features)}\n\n")
    f.write("PERFORMANCE METRICS\n")
    f.write("-" * 60 + "\n")
    f.write(f"Accuracy:   {accuracy * 100:.2f}%\n")
    f.write(f"Precision:  {precision * 100:.2f}%\n")
    f.write(f"Recall:     {recall * 100:.2f}%\n")
    f.write(f"F1 Score:   {f1 * 100:.2f}%\n\n")
    f.write("CONFUSION MATRIX\n")
    f.write("-" * 60 + "\n")
    f.write(str(cm) + "\n\n")
    f.write("CLASSIFICATION REPORT\n")
    f.write("-" * 60 + "\n")
    f.write(classification_report(y_test, y_pred, zero_division=0))

print(f"✅ Report saved: {report_file}")

print("\n" + "=" * 60)
print(" 🎉 TRAINING COMPLETE!")
print("=" * 60)