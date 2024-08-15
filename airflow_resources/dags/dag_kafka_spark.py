from datetime import timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime

from src.weather_client.weather_data import fetch_weather_data  # Updated to match the OpenWeather API context

start_date = datetime.today() - timedelta(days=1)

default_args = {
    "owner": "airflow",
    "start_date": start_date,
    "retries": 1,  # Number of retries before failing the task
    "retry_delay": timedelta(seconds=5),
}

with DAG(
    dag_id="weather_data_processing_dag",  # Updated DAG ID
    default_args=default_args,
    schedule_interval=timedelta(days=1),
    catchup=False,
) as dag:

    weather_fetch_task = PythonOperator(
        task_id="fetch_weather_data",  # Updated task ID
        python_callable=fetch_weather_data,  # Updated callable to fetch weather data
        dag=dag,
    )

    spark_processing_task = DockerOperator(
        task_id="pyspark_weather_processing",  # Updated task ID
        image="weather-data/spark:latest",  # Updated Docker image name
        api_version="auto",
        auto_remove=True,
        command="./bin/spark-submit --master local[*] --packages org.postgresql:postgresql:42.5.4 ./spark_weather_processing.py",  # Updated Spark command
        docker_url='tcp://docker-proxy:2375',
        environment={'SPARK_LOCAL_HOSTNAME': 'localhost'},
        network_mode="airflow-weather",  # Updated network mode
        dag=dag,
    )

    weather_fetch_task >> spark_processing_task  # Updated task dependency
