import pandas as pd
import psycopg2

#Declare csv path to be read

CSV_PATH = "/opt/airflow/data/cleaned_aggregated_data.csv"

#Declare connection with PostgreSQL
DB_CONFIG = {
    "host": "host.docker.internal",  # Use docker internal when running inside docker container
    "port": "5432",
    "database": "postgres",
    "user": "de_admin",
    "password": "rizky_eyds"
}

#Declare target table name in PostgreSQL
TABLE_NAME = "customer_aggregates"

#Function to connect to PostgreSQL based on DBCONFIG above
def connect_to_postgres():
    return psycopg2.connect(**DB_CONFIG)

#Function to ensure tables exists before writing data in PostgreSQL
def ensure_table_exists(cursor):
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            customer_id TEXT PRIMARY KEY,
            total_transactions INT,
            total_amount NUMERIC
        );
    """)

#Perform upsert data to target table in PostgreSQL
def upsert_aggregated_data(cursor, csv_path):
    df = pd.read_csv(csv_path)
    df["customer_id"] = df["customer_id"].astype(str)

    upsert_query = f"""
        INSERT INTO {TABLE_NAME} (customer_id, total_transactions, total_amount)
        VALUES (%s, %s, %s)
        ON CONFLICT (customer_id) DO UPDATE SET
            total_transactions = EXCLUDED.total_transactions,
            total_amount = EXCLUDED.total_amount;
    """

    for _, row in df.iterrows():
        cursor.execute(upsert_query, (
            row["customer_id"],
            row["total_transactions"],
            row["total_amount"]
        ))

#Declare function sequence to perform data writing into PostgreSQL
def main():
    conn = connect_to_postgres()
    cursor = conn.cursor()
    try:
        ensure_table_exists(cursor)
        upsert_aggregated_data(cursor, CSV_PATH)
        conn.commit()
        print("✅ Aggregated data successfully inserted/updated in PostgreSQL")
    except Exception as e:
        print("❌ Error:", e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
