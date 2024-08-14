import os

# API params
PATH_LAST_PROCESSED = "./data/last_weather_processed.json"  # Changed to reflect weather data processing
MAX_LIMIT = 100
MAX_OFFSET = 10000

# We have three parameters in the URL:
# 1. MAX_LIMIT: the maximum number of records to be returned by the API (not directly applicable to OpenWeather, but kept for consistency)
# 2. CITY_NAME: the city for which we want to get the weather data
# 3. API_KEY: the key to authenticate with the OpenWeather API
CITY_NAME = "Chicago"
API_KEY = os.getenv("OPENWEATHER_API_KEY", "your_default_api_key")
URL_API = "http://api.openweathermap.org/data/2.5/weather?q={}&appid={}"
URL_API = URL_API.format(CITY_NAME, API_KEY)

# POSTGRES PARAMS
user_name = os.getenv("POSTGRES_DOCKER_USER", "localhost")
POSTGRES_URL = f"jdbc:postgresql://{user_name}:5432/weather_db"  # Changed the database name to 'weather_db'
POSTGRES_PROPERTIES = {
    "user": "postgres",
    "password": os.getenv("POSTGRES_PASSWORD"),
    "driver": "org.postgresql.Driver",
}

# Columns specific to the weather data that might be new
NEW_COLUMNS = [
    "weather_description",
    "temperature",
    "humidity",
    "pressure",
    "wind_speed",
]

# Columns to normalize from the weather data response
COLUMNS_TO_NORMALIZE = [
    "weather",
    "main",
    "wind",
    "clouds",
    "sys",
]

# Columns to keep from the weather data response
COLUMNS_TO_KEEP = [
    "id",
    "name",
    "coord",
    "weather",
    "main",
    "visibility",
    "wind",
    "clouds",
    "dt",
    "sys",
]
DB_FIELDS = COLUMNS_TO_KEEP + COLUMNS_TO_NORMALIZE + NEW_COLUMNS
