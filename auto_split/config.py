import os

from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv("DEBUG", True)
BASE_URL = os.getenv("BASE_URL", "http://localhost:5001")
DATABASE = os.getenv("DATABASE", "data/carpool.db")
