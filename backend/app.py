# =====================================================
# SMARTLOAN TRIGGER - MAIN FLASK APPLICATION
# PART 1: IMPORTS + SETUP
# =====================================================

from flask import Flask, render_template, jsonify, request
import pandas as pd
import joblib
import os
import sys
from datetime import datetime


# =====================================================
# FLASK APPLICATION
# =====================================================

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static"
)


# =====================================================
# PATHS
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))


# =====================================================
# DATABASE
# =====================================================

DATABASE_DIR = os.path.join(PROJECT_ROOT, "database")

if DATABASE_DIR not in sys.path:
    sys.path.append(DATABASE_DIR)

from db import create_database, get_connection

# Initialize database
create_database()


# =====================================================
# FILE PATHS
# =====================================================

MODEL_FILE = os.path.join(
    PROJECT_ROOT, "models", "smartloan_model.pkl"
)

PROFILE_DATA_FILE = os.path.join(
    PROJECT_ROOT, "data", "processed",
    "smartloan_customer_profile.csv"
)

MODEL_DATA_FILE = os.path.join(
    PROJECT_ROOT, "data", "processed",
    "smartloan_features.csv"
)


# =====================================================
# LOAD MODEL + DATASETS
# =====================================================

model = None
profile_df = None
model_df = None

try:
    model = joblib.load(MODEL_FILE)
    profile_df = pd.read_csv(PROFILE_DATA_FILE)
    model_df = pd.read_csv(MODEL_DATA_FILE)

    print("=" * 50)
    print("SmartLoan Trigger Backend")
    print("=" * 50)
    print("✅ Model loaded successfully")
    print("✅ Dashboard dataset loaded successfully")
    print("✅ Model dataset loaded successfully")
    print(f"   Customers: {len(profile_df)}")
    print(f"   Profile columns: {len(profile_df.columns)}")
    print(f"   Model columns: {len(model_df.columns)}")
    print("=" * 50)

except Exception as e:
    print("=" * 50)
    print("❌ ERROR LOADING BACKEND DATA")
    print("=" * 50)
    print(e)
    print(f"Model path: {MODEL_FILE}")
    print(f"Profile dataset: {PROFILE_DATA_FILE}")
    print(f"Model dataset: {MODEL_DATA_FILE}")
    print("=" * 50)
    # =====================================================
# HELPER FUNCTIONS
# =====================================================

def make_customer_id(number):
    """Customer number se C00001 format banao"""
    return f"C{str(number).zfill(5)}"


def parse_customer_id(customer_id):
    """C00001 ya 1 se number nikalo"""
    try:
        cleaned = str(customer_id).strip().lstrip("Cc")
        return int(cleaned)
    except (ValueError, AttributeError):
        return None


def classify_by_balance(balance):
    """
    Balance ke basis pe customer class return karo
    
    Rule:
        Balance < 2000          → LOW
        2000 ≤ Balance < 5000   → MEDIUM
        Balance ≥ 5000          → HIGH
    """
    try:
        b = float(balance)
    except (ValueError, TypeError):
        return "LOW"

    if b < 2000:
        return "LOW"
    elif b < 5000:
        return "MEDIUM"
    else:
        return "HIGH"


def get_customer_class(row):
    """
    Strictly Balance-based classification.
    LOW: Balance < 2000
    MEDIUM: 2000 <= Balance < 5000
    HIGH: Balance >= 5000
    """
    try:
        balance = float(row.get("balance", 0))
    except (ValueError, TypeError):
        balance = 0

    if balance < 2000:
        return "LOW"
    elif balance < 5000:
        return "MEDIUM"
    else:
        return "HIGH"


def get_channel_for_class(customer_class):
    """
    Class ke hisaab se recommended channel return karo
    """
    if customer_class == "HIGH":
        return "Phone / SMS"
    elif customer_class == "MEDIUM":
        return "SMS"
    else:
        return "Occasional SMS"


def get_offers_for_class(customer_class):
    """
    Class ke hisaab se offers list return karo
    """
    offers = {
        "LOW": [
            "Basic Savings Account",
            "Occasional SMS Offers",
            "Standard Debit Card",
            "Micro Loan (up to ₹10,000)"
        ],
        "MEDIUM": [
            "Premium Savings Account",
            "Regular Credit Card",
            "Personal Loan (up to ₹50,000)",
            "Fixed Deposit - Special Rate",
            "Free SMS Alerts"
        ],
        "HIGH": [
            "💰 Wealth Management (Shares, Mutual Funds, Real Estate)",
            "🧾 Free Tax Advisory",
            "💳 Super-Premium Credit Card (HDFC Infinia / SBI Elite)",
            "🔐 Free Locker / 50% Discount",
            "💱 Low Forex Markup (0-1%)",
            "📉 Business Loan Special Rate",
            "🎬 Free Movie Tickets + Concierge Service",
            "✈️ Free International Airport Lounge Access",
            "🏨 Luxury Hotel Memberships",
            "⛳ Free Golf Course Entry"
        ]
    }
    return offers.get(customer_class, [])


def calculate_emi(principal, annual_rate, months):
    """
    EMI calculate karo
    
    Formula:
        EMI = [P × r × (1+r)^n] / [(1+r)^n − 1]
    """
    try:
        P = float(principal)
        R = float(annual_rate)
        N = int(months)

        if P <= 0 or R < 0 or N <= 0:
            return None

        r = R / 12 / 100

        if r == 0:
            emi = P / N
        else:
            emi = (P * r * ((1 + r) ** N)) / (((1 + r) ** N) - 1)

        total_payment = emi * N
        total_interest = total_payment - P

        return {
            "emi": round(emi, 2),
            "total_payment": round(total_payment, 2),
            "total_interest": round(total_interest, 2),
            "principal": round(P, 2),
            "months": N
        }
    except (ValueError, TypeError, ZeroDivisionError):
        return None
    # =====================================================
# ROUTE: HOME PAGE
# =====================================================

@app.route("/")
def home():
    return render_template("index.html")


# =====================================================
# ROUTE: GET ALL CUSTOMERS
# =====================================================

@app.route("/api/customers")
def get_customers():
    if profile_df is None:
        return jsonify({
            "success": False,
            "error": "Backend data could not be loaded"
        }), 500

    data = profile_df.copy()

    # Customer ID banao
    if "customer_id" not in data.columns:
        data.insert(
            0, "customer_id",
            [make_customer_id(i + 1) for i in range(len(data))]
        )
    else:
        data["customer_id"] = data["customer_id"].astype(str)

    # Class add karo (balance-based)
    data["customer_class"] = data.apply(get_customer_class, axis=1)

    # RIGHT-TIME SCORE SET KARO
    if "right_time_score" not in data.columns:
        if "financial_potential_score" in data.columns:
            data["right_time_score"] = pd.to_numeric(
                data["financial_potential_score"], errors="coerce"
            ).fillna(0).astype(int)
        elif "financial_activity_score" in data.columns:
            data["right_time_score"] = pd.to_numeric(
                data["financial_activity_score"], errors="coerce"
            ).fillna(0).astype(int)
        else:
            data["right_time_score"] = data["balance"].apply(
                lambda b: min(100, max(10, int(float(b) / 100)))
                if pd.notna(b) else 0
            )

    # Channel add karo
    data["channel"] = data["customer_class"].apply(get_channel_for_class)

    # Recommended action bhi class ke basis pe
    def get_action(customer_class):
        if customer_class == "HIGH":
            return "Contact Now"
        elif customer_class == "MEDIUM":
            return "Soft Reminder"
        else:
            return "Occasional Offer"

    data["recommended_action"] = data["customer_class"].apply(get_action)

    # Dashboard columns
    dashboard_columns = [
        "customer_id", "age", "job", "marital", "education",
        "balance", "housing", "loan", "contact",
        "monthly_income", "monthly_spending", "monthly_transactions",
        "investment_amount", "emi_amount", "savings_amount",
        "digital_payment_count", "loan_repayment_status",
        "spending_frequency", "financial_activity_score",
        "financial_potential_score", "customer_class", "customer_category",
        "contact_frequency", "next_contact_days",
        "recently_contacted", "prev_success", "high_engagement",
        "healthy_balance", "right_time_score",
        "duration", "campaign", "pdays", "previous", "poutcome",
        "recommended_action", "channel", "deposit"
    ]

    available = [c for c in dashboard_columns if c in data.columns]
    data = data[available].fillna("")

    return jsonify({
        "success": True,
        "count": len(data),
        "stats": {
            "LOW": int((data["customer_class"] == "LOW").sum()),
            "MEDIUM": int((data["customer_class"] == "MEDIUM").sum()),
            "HIGH": int((data["customer_class"] == "HIGH").sum())
        },
        "customers": data.to_dict(orient="records")
    })
# =====================================================
# ROUTE: GET SINGLE CUSTOMER
# =====================================================

@app.route("/api/customer/<int:customer_id>")
def get_customer(customer_id):
    if profile_df is None:
        return jsonify({
            "success": False,
            "error": "Dataset not loaded"
        }), 500

    if customer_id < 1 or customer_id > len(profile_df):
        return jsonify({
            "success": False,
            "error": "Customer not found"
        }), 404

    customer = profile_df.iloc[customer_id - 1].fillna("").to_dict()
    customer["customer_id"] = make_customer_id(customer_id)

    c_class = get_customer_class(customer)
    customer["customer_class"] = c_class
    customer["channel"] = get_channel_for_class(c_class)
    customer["offers"] = get_offers_for_class(c_class)

    return jsonify({
        "success": True,
        "customer": customer
    })


# =====================================================
# ROUTE: PREDICT CUSTOMER
# =====================================================

@app.route("/api/predict/<int:customer_id>")
def predict(customer_id):
    if model_df is None or model is None:
        return jsonify({
            "success": False,
            "error": "Model or dataset not loaded"
        }), 500

    if customer_id < 1 or customer_id > len(model_df):
        return jsonify({
            "success": False,
            "error": "Customer not found"
        }), 404

    customer = model_df.iloc[[customer_id - 1]].copy()

    features = [
        "age", "job", "marital", "education", "default",
        "balance", "housing", "loan", "contact",
        "day", "month", "duration", "campaign",
        "pdays", "previous", "poutcome",
        "recently_contacted", "prev_success",
        "high_engagement", "healthy_balance",
        "right_time_score"
    ]

    missing = [c for c in features if c not in customer.columns]

    if missing:
        return jsonify({
            "success": False,
            "error": "Missing model features",
            "missing": missing
        }), 500

    X = customer[features]

    try:
        prediction = model.predict(X)[0]

        if hasattr(model, "predict_proba"):
            probability = model.predict_proba(X)[0][1]
        else:
            probability = 0

        profile_customer = profile_df.iloc[customer_id - 1].copy()

        def safe_value(column, default=""):
            if column in profile_customer.index:
                value = profile_customer[column]
                if pd.isna(value):
                    return default
                return value
            return default

        c_class = get_customer_class(profile_customer.to_dict())

        return jsonify({
            "success": True,
            "customer_id": make_customer_id(customer_id),
            "age": int(customer["age"].iloc[0]),
            "job": str(customer["job"].iloc[0]),
            "marital": str(customer["marital"].iloc[0]),
            "education": str(customer["education"].iloc[0]),
            "balance": int(customer["balance"].iloc[0]),
            "customer_class": c_class,
            "channel": get_channel_for_class(c_class),
            "offers": get_offers_for_class(c_class),
            "right_time_score": int(customer["right_time_score"].iloc[0]),
            "recommended_action": str(customer["recommended_action"].iloc[0]),
            "financial_activity_score": safe_value("financial_activity_score"),
            "financial_potential_score": safe_value("financial_potential_score"),
            "customer_category": safe_value("customer_category"),
            "contact_frequency": safe_value("contact_frequency"),
            "next_contact_days": safe_value("next_contact_days"),
            "monthly_income": safe_value("monthly_income"),
            "monthly_spending": safe_value("monthly_spending"),
            "investment_amount": safe_value("investment_amount"),
            "emi_amount": safe_value("emi_amount"),
            "prediction": (
                "Likely to accept" if prediction == 1
                else "Unlikely to accept"
            ),
            "acceptance_probability": round(probability * 100, 2)
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    # =====================================================
# ROUTE: CUSTOMER ACTION (CALL / SMS)
# =====================================================

@app.route("/api/action", methods=["POST"])
def customer_action():
    if profile_df is None:
        return jsonify({
            "success": False,
            "error": "Dataset not loaded"
        }), 500

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "error": "No action data received"
        }), 400

    customer_id = str(data.get("customer_id", "")).strip()
    action_type = str(data.get("action_type", "")).strip().lower()
    channel = str(data.get("channel", "")).strip()
    message = str(data.get("message", "")).strip()

    if not customer_id:
        return jsonify({
            "success": False,
            "error": "Customer ID is required"
        }), 400

    customer_number = parse_customer_id(customer_id)

    if customer_number is None:
        return jsonify({
            "success": False,
            "error": "Invalid customer ID format"
        }), 400

    if customer_number < 1 or customer_number > len(profile_df):
        return jsonify({
            "success": False,
            "error": "Customer not found"
        }), 404

    allowed_actions = ["call", "sms"]

    if action_type not in allowed_actions:
        return jsonify({
            "success": False,
            "error": "Invalid action. Use 'call' or 'sms'."
        }), 400

    if not channel:
        channel = "Call" if action_type == "call" else "SMS"

    if not message:
        if action_type == "call":
            message = "Customer contacted by SmartLoan Trigger."
        else:
            message = "SmartLoan offer SMS sent to customer."

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO action_history
            (customer_id, action_type, channel, message, status)
            VALUES (?, ?, ?, ?, ?)
        """, (customer_id, action_type, channel, message, "Completed"))

        conn.commit()
        action_id = cursor.lastrowid
        conn.close()

        return jsonify({
            "success": True,
            "message": "Customer action saved successfully",
            "action_id": action_id,
            "customer_id": customer_id,
            "action_type": action_type,
            "channel": channel,
            "status": "Completed",
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Database error: {str(e)}"
        }), 500


# =====================================================
# ROUTE: CREATE LOAN OFFER (With EMI Calculation)
# =====================================================

@app.route("/api/create-offer", methods=["POST"])
def create_offer():
    if profile_df is None:
        return jsonify({
            "success": False,
            "error": "Dataset not loaded"
        }), 500

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "error": "No offer data received"
        }), 400

    customer_id = str(data.get("customer_id", "")).strip()
    offer_type = str(data.get("offer_type", "Personal Loan")).strip()
    amount = data.get("amount")
    interest_rate = data.get("interest_rate")
    tenure = data.get("tenure")
    channel = str(data.get("channel", "App")).strip()
    message = str(data.get("message", "")).strip()

    if not customer_id:
        return jsonify({
            "success": False,
            "error": "Customer ID is required"
        }), 400

    customer_number = parse_customer_id(customer_id)

    if customer_number is None:
        return jsonify({
            "success": False,
            "error": "Invalid customer ID format"
        }), 400

    if customer_number < 1 or customer_number > len(profile_df):
        return jsonify({
            "success": False,
            "error": "Customer not found"
        }), 404

    try:
        amount = int(amount)
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "error": "Loan amount must be a number"
        }), 400

    try:
        interest_rate = float(interest_rate)
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "error": "Interest rate must be a number"
        }), 400

    try:
        tenure = int(tenure)
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "error": "Tenure must be a number"
        }), 400

    if amount < 10000 or amount > 200000:
        return jsonify({
            "success": False,
            "error": "Loan amount must be between ₹10,000 and ₹2,00,000"
        }), 400

    if interest_rate < 1 or interest_rate > 30:
        return jsonify({
            "success": False,
            "error": "Interest rate must be between 1% and 30%"
        }), 400

    if tenure < 1 or tenure > 120:
        return jsonify({
            "success": False,
            "error": "Tenure must be between 1 and 120 months"
        }), 400

    emi_data = calculate_emi(amount, interest_rate, tenure)

    if emi_data is None:
        return jsonify({
            "success": False,
            "error": "EMI calculation failed"
        }), 400

    if not message:
        message = (
            f"SmartLoan offer: ₹{amount:,} at {interest_rate}% "
            f"interest for {tenure} months. "
            f"EMI: ₹{emi_data['emi']:,}"
        )

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO offer_history
            (customer_id, offer_type, amount, interest_rate,
             tenure, channel, message, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            customer_id, offer_type, amount, interest_rate,
            tenure, channel, message, "Sent"
        ))

        conn.commit()
        offer_id = cursor.lastrowid
        conn.close()

        return jsonify({
            "success": True,
            "message": "Loan offer created successfully",
            "offer_id": offer_id,
            "customer_id": customer_id,
            "offer_type": offer_type,
            "amount": amount,
            "interest_rate": interest_rate,
            "tenure": tenure,
            "channel": channel,
            "status": "Sent",
            "emi_details": emi_data,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Database error: {str(e)}"
        }), 500


# =====================================================
# ROUTE: EMI CALCULATOR (Sirf Calculate)
# =====================================================

@app.route("/api/calculate-emi", methods=["POST"])
def calculate_emi_api():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "error": "No data received"
        }), 400

    try:
        amount = float(data.get("amount", 0))
        interest_rate = float(data.get("interest_rate", 0))
        tenure = int(data.get("tenure", 0))
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "error": "Invalid input values"
        }), 400

    if amount <= 0 or interest_rate < 0 or tenure <= 0:
        return jsonify({
            "success": False,
            "error": "All values must be positive"
        }), 400

    emi_data = calculate_emi(amount, interest_rate, tenure)

    if emi_data is None:
        return jsonify({
            "success": False,
            "error": "Calculation failed"
        }), 400

    return jsonify({
        "success": True,
        "emi_details": emi_data
    })
# =====================================================
# ROUTE: GET ACTION HISTORY
# =====================================================

@app.route("/api/action-history/<customer_id>")
def get_action_history(customer_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, customer_id, action_type, channel,
                   message, status, created_at
            FROM action_history
            WHERE customer_id = ?
            ORDER BY id DESC
        """, (customer_id,))

        rows = cursor.fetchall()
        conn.close()

        history = [{
            "id": r[0], "customer_id": r[1], "action_type": r[2],
            "channel": r[3], "message": r[4], "status": r[5],
            "created_at": r[6]
        } for r in rows]

        return jsonify({
            "success": True,
            "count": len(history),
            "history": history
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =====================================================
# ROUTE: GET OFFER HISTORY
# =====================================================

@app.route("/api/offer-history/<customer_id>")
def get_offer_history(customer_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, customer_id, offer_type, amount,
                   interest_rate, tenure, channel,
                   message, status, created_at
            FROM offer_history
            WHERE customer_id = ?
            ORDER BY id DESC
        """, (customer_id,))

        rows = cursor.fetchall()
        conn.close()

        history = [{
            "id": r[0], "customer_id": r[1], "offer_type": r[2],
            "amount": r[3], "interest_rate": r[4], "tenure": r[5],
            "channel": r[6], "message": r[7], "status": r[8],
            "created_at": r[9]
        } for r in rows]

        return jsonify({
            "success": True,
            "count": len(history),
            "history": history
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =====================================================
# ROUTE: COMPLETE CUSTOMER HISTORY
# =====================================================

@app.route("/api/customer-history/<customer_id>")
def get_customer_history(customer_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, customer_id, action_type, channel,
                   message, status, created_at
            FROM action_history
            WHERE customer_id = ?
            ORDER BY id DESC
        """, (customer_id,))
        action_rows = cursor.fetchall()

        cursor.execute("""
            SELECT id, customer_id, offer_type, amount,
                   interest_rate, tenure, channel,
                   message, status, created_at
            FROM offer_history
            WHERE customer_id = ?
            ORDER BY id DESC
        """, (customer_id,))
        offer_rows = cursor.fetchall()

        conn.close()

        actions = [{
            "id": r[0], "customer_id": r[1], "action_type": r[2],
            "channel": r[3], "message": r[4], "status": r[5],
            "created_at": r[6]
        } for r in action_rows]

        offers = [{
            "id": r[0], "customer_id": r[1], "offer_type": r[2],
            "amount": r[3], "interest_rate": r[4], "tenure": r[5],
            "channel": r[6], "message": r[7], "status": r[8],
            "created_at": r[9]
        } for r in offer_rows]

        return jsonify({
            "success": True,
            "customer_id": customer_id,
            "actions": actions,
            "offers": offers
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =====================================================
# ROUTE: OFFERS BY CLASS
# =====================================================

@app.route("/api/offers/<customer_class>")
def get_offers_by_class(customer_class):
    customer_class = customer_class.upper()

    if customer_class not in ["LOW", "MEDIUM", "HIGH"]:
        return jsonify({
            "success": False,
            "error": "Invalid class. Use LOW, MEDIUM, or HIGH."
        }), 400

    return jsonify({
        "success": True,
        "class": customer_class,
        "offers": get_offers_for_class(customer_class)
    })


# =====================================================
# ROUTE: HEALTH CHECK
# =====================================================

@app.route("/api/health")
def health():
    return jsonify({
        "success": True,
        "backend": "running",
        "model_loaded": model is not None,
        "profile_dataset_loaded": profile_df is not None,
        "model_dataset_loaded": model_df is not None,
        "customers": len(profile_df) if profile_df is not None else 0
    })


# =====================================================
# RUN FLASK
# =====================================================

if __name__ == "__main__":
    print("🚀 Starting Flask Server...")
    print("🌐 Open: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)