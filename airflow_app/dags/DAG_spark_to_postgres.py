from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    dag_id='spark_to_postgres_dag',
    default_args=default_args,
    description='Clean data with PySpark then upsert to PostgreSQL',
    start_date=days_ago(1),
    schedule_interval=None,  # Change to '@daily' or cron if needed
    catchup=False,
    tags=['pyspark', 'postgres'],
) as dag:

    run_spark = BashOperator(
        task_id='run_spark_processing',
        bash_command='python /opt/airflow/dags/helpers/pyspark_dataproc.py'
    )

    upsert_to_postgres = BashOperator(
        task_id='upsert_to_postgres',
        bash_command='python /opt/airflow/dags/helpers/insert_to_postgres.py'
    )

    run_spark >> upsert_to_postgres
