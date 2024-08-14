from src.constants import (
    URL_API,
    PATH_LAST_PROCESSED,
    MAX_LIMIT,
    MAX_OFFSET,
)

from .transformations import transform_row

import kafka.errors
import json
import datetime
import requests
from kafka import KafkaProducer
from typing import List
import logging

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO, force=True)


def get_latest_timestamp():
    """
    Gets the latest timestamp from the last_weather_processed.json file
    """
    with open(PATH_LAST_PROCESSED, "r") as file:
        data = json.load(file)
        if "last_processed" in data:
            return data["last_processed"]
        else:
            return datetime.datetime.min


def update_last_processed_file(data: dict):
    """
    Updates the last_weather_processed.json file with the latest timestamp.
    Since the comparison is based on the weather data retrieval time, 
    we set the new last_processed timestamp to the current retrieval time.
    """
    last_processed = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    with open(PATH_LAST_PROCESSED, "w") as file:
        json.dump({"last_processed": last_processed}, file)


def get_all_data() -> List[dict]:
    """
    Fetches weather data from the OpenWeather API.
    Since OpenWeather returns data for a single city, we handle this in a single request.
    """
    url = URL_API
    response = requests.get(url)
    data = response.json()
    full_data = [data]

    logging.info(f"Got weather data from the API for city: {data.get('name', 'unknown')}")

    return full_data


def deduplicate_data(data: List[dict]) -> List[dict]:
    """
    Deduplication might not be necessary for weather data, but this is a placeholder.
    """
    return data  # Keeping as-is since it's a single API call per city


def query_data() -> List[dict]:
    """
    Queries the weather data from the OpenWeather API
    """
    last_processed = get_latest_timestamp()
    full_data = get_all_data()
    full_data = deduplicate_data(full_data)
    if full_data:
        update_last_processed_file(full_data[0])
    return full_data


def process_data(row):
    """
    Processes the weather data from the API
    """
    return transform_row(row)


def create_kafka_producer():
    """
    Creates the Kafka producer object
    """
    try:
        producer = KafkaProducer(bootstrap_servers=["kafka:9092"])
    except kafka.errors.NoBrokersAvailable:
        logging.info(
            "We assume that we are running locally, so we use localhost instead of kafka and the external "
            "port 9094"
        )
        producer = KafkaProducer(bootstrap_servers=["localhost:9094"])

    return producer


def stream():
    """
    Writes the API weather data to Kafka topic weather_data
    """
    producer = create_kafka_producer()
    results = query_data()
    kafka_data_full = map(process_data, results)
    for kafka_data in kafka_data_full:
        producer.send("weather_data", json.dumps(kafka_data).encode("utf-8"))


if __name__ == "__main__":
    stream()
