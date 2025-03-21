from pyspark.sql import SparkSession
import pandas as pd

# Initialize Spark
spark = SparkSession.builder.appName("NoHadoopCSVExport").getOrCreate()

# Read JSON
df = spark.read.json(
    r"C:\Users\user\OneDrive\RFA _Personal Files\02. COURSE\Purwadhika_Data Engineering\Purwadhika_VS\EYDS_TEST\airflow_app\data\sample_data.json",
    multiLine=True
)

# Clean data: drop rows with any nulls, then drop duplicates
df_cleaned = df.dropna().dropDuplicates()

# Convert to pandas for export
df_pandas = df_cleaned.toPandas()

# Fix column order
columns_order = ["transaction_id", "customer_id", "timestamp", "amount", "currency", "status"]
df_pandas = df_pandas[columns_order]

# Save to CSV
df_pandas.to_csv(
    r"C:\Users\user\OneDrive\RFA _Personal Files\02. COURSE\Purwadhika_Data Engineering\Purwadhika_VS\EYDS_TEST\airflow_app\data\cleaned_data.csv",
    index=False
)

spark.stop()
print("✅ Nulls dropped, duplicates removed, and CSV exported with correct column order!")
