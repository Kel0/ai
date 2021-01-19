from decouple import config
from pathlib import Path


ABS_PATH = Path().resolve()

DB_URL = config("DB_URL", cast=str)
WEATHER_API_LINK = config("WEATHER_API_LINK", cast=str)
WEATHER_API_TOKEN = config("WEATHER_API_TOKEN", cast=str)
WIKI_BASE_URL = config("WIKI_BASE_URL", cast=str)
WIKI_CITY_POSTFIX = config("WIKI_CITY_POSTFIX", cast=str)
