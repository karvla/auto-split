import os

from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv("DEBUG")

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
CALENDAR_SECRET = os.getenv("CALENDAR_SECRET")

USERS = os.getenv("USERS").split(",") if os.getenv("USERS") else []
CURRENCY = os.getenv("CURRENCY")
DISTANCE_UNIT = os.getenv("DISTANCE_UNIT")
VOLUME_UNIT = os.getenv("VOLUME_UNIT")
FUEL_EFFICIENCY = float(os.getenv("FUEL_EFFICIENCY", 0))
COST_PER_DISTANCE = float(os.getenv("COST_PER_DISTANCE", 0))

BASE_URL = os.getenv("BASE_URL")
