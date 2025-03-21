import pandas as pd
import psycopg2


# === CONFIGURATION ===
CSV_PATH = r"C:\Users\user\OneDrive\RFA _Personal Files\02. COURSE\Purwadhika_Data Engineering\Purwadhika_VS\EYDS_TEST\airflow_app\data\cleaned_data.csv"

DB_CONFIG = {
    "host": "host.docker.internal",      # Use 'postgres' if inside Docker
    "port": "5432",           # Update if using a different mapped port
    "database": "postgres",
    "user": "de_admin",
    "password": "rizky_eyds"
}

TABLE_NAME = "transactions"


# === FUNCTIONS ===

def connect_to_postgres():
    """Establish and return a PostgreSQL database connection."""
    return psycopg2.connect(**DB_CONFIG)


def ensure_table_exists(cursor):
    """Create the table if it does not already exist."""
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        transaction_id TEXT PRIMARY KEY,
        customer_id TEXT,
        timestamp TIMESTAMP,
        amount NUMERIC,
        currency TEXT,
        status TEXT
    );
    """
    cursor.execute(create_table_query)


def load_csv_and_upsert(cursor, csv_path):
    """Load cleaned CSV data and perform UPSERT into PostgreSQL."""
    # Load and clean the CSV
    df = pd.read_csv(csv_path)

    # Ensure correct types
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["customer_id"] = df["customer_id"].astype(int)
    df["transaction_id"] = df["transaction_id"].astype(str)
    df["currency"] = df["currency"].astype(str)
    df["status"] = df["status"].astype(str)

    # Drop rows with invalid timestamp or amount
    df = df.dropna(subset=["amount", "timestamp"])

    # Upsert each row
    upsert_query = f"""
    INSERT INTO {TABLE_NAME} (
        transaction_id, customer_id, timestamp, amount, currency, status
    )
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (transaction_id)
    DO UPDATE SET
        customer_id = EXCLUDED.customer_id,
        timestamp = EXCLUDED.timestamp,
        amount = EXCLUDED.amount,
        currency = EXCLUDED.currency,
        status = EXCLUDED.status;
    """

    for _, row in df.iterrows():
        cursor.execute(upsert_query, (
            row["transaction_id"],
            row["customer_id"],
            row["timestamp"],
            row["amount"],
            row["currency"],
            row["status"]
        ))


def main():
    try:
        conn = connect_to_postgres()
        cursor = conn.cursor()

        # Ensure table exists
        ensure_table_exists(cursor)

        # Load CSV and perform UPSERT
        load_csv_and_upsert(cursor, CSV_PATH)

        conn.commit()
        print("✅ Data successfully inserted (or updated) in PostgreSQL.")

    except Exception as e:
        print("❌ Error:", e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


# === EXECUTE SCRIPT ===
if __name__ == "__main__":
    main()
