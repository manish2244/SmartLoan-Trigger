import sqlite3
import os

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DB_PATH = os.path.join(
    BASE_DIR,
    "database",
    "smartloan.db"
)


def get_connection():

    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    return conn


def create_database():

    conn = get_connection()

    cursor = conn.cursor()

    # =================================================
    # OFFER HISTORY
    # =================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS offer_history (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            customer_id TEXT NOT NULL,

            offer_type TEXT NOT NULL,

            amount INTEGER,

            interest_rate REAL,

            tenure INTEGER,

            channel TEXT,

            message TEXT,

            status TEXT,

            created_at
            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


    # =================================================
    # ACTION HISTORY
    # =================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS action_history (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            customer_id TEXT NOT NULL,

            action_type TEXT NOT NULL,

            channel TEXT,

            message TEXT,

            status TEXT,

            created_at
            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


    # =================================================
    # COMMIT
    # =================================================

    conn.commit()

    conn.close()


    print("========================================")
    print("SmartLoan Trigger Database")
    print("========================================")
    print("Database created successfully")
    print("Database path:")
    print(DB_PATH)
    print("========================================")


if __name__ == "__main__":

    create_database()