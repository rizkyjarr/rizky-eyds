from pyspark.sql import SparkSession
from pyspark.sql.functions import count, sum
import pandas as pd

#Initialize spark session
spark = SparkSession.builder.appName("AggregatedSparkToCSV").getOrCreate()

#Read JSON files from aiflow volume
df = spark.read.json("/opt/airflow/data/sample_data.json", multiLine=True)

#Data cleaning: drop rows with null values and duplicated records
df_cleaned = df.dropna().dropDuplicates()

#Aggregating data based on customer, to sum total transactions and total amounts
df_agg = df_cleaned.groupBy("customer_id").agg(
    count("transaction_id").alias("total_transactions"),
    sum("amount").alias("total_amount")
)

#Export pyspark data frame to pandas and export to csv -- i still havent managed to write data from JSON to Postgre using PySpark
df_agg.toPandas().to_csv("/opt/airflow/data/cleaned_aggregated_data.csv", index=False)

#Close PySpark session
spark.stop()
print("✅ Aggregated data exported to CSV!")