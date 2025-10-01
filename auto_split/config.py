import os

from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://localhost:5001")
DEBUG = "localhost" in BASE_URL
DATABASE = os.getenv("DATABASE", "data/carpool.db")
