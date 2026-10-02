# 🏦 SmartLoan Trigger — Banking CRM System

An intelligent, full-stack Banking CRM platform that leverages Machine Learning to segment customers, manage offers, and process loans dynamically.

## 📌 Project Overview

Banks need a smart way to understand which customers should be targeted for which offers. **SmartLoan Trigger** solves this by analyzing customer data and segmenting them into **Low, Middle, and High-income classes** based on their balance. It provides a dashboard for bank employees to manage interactions, send SMS, make calls, calculate EMIs, and maintain a complete audit history.

## 🚀 Key Features

*   **Intelligent Customer Segmentation:** 
    *   🟢 **Low Income:** Balance < ₹2,000
    *   🟡 **Middle Income:** Balance ₹2,000 – ₹5,000
    *   🔵 **High Income / HNI:** Balance > ₹5,000
*   **Dynamic Offer Engine:** Displays class-specific offers.
*   **Customer Interaction Panel:** Call simulation with live timer and SMS system with class-based templates.
*   **Loan Calculator & EMI System:** Real-time EMI calculation.
*   **Activity History:** Complete audit trail of all interactions.
*   **Analytics Dashboard:** Visual representation using Chart.js.

## 🛠️ Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python, Flask |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Database** | SQLite3 |
| **Data Processing & ML** | Pandas, Scikit-learn, Joblib |
| **Data Visualization** | Chart.js |
| **Tools** | Git, GitHub, VS Code |

## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/manish2244/SmartLoan-Trigger.git
   cd SmartLoan-Trigger
