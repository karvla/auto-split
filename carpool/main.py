# pylint: skip-file
from db.init_db import run_db_migrations
from dotenv import load_dotenv

load_dotenv()
run_db_migrations()
import importlib

import bookings
import bookings_calendar
import debts
import expenses
import login
from app import app
from fasthtml.common import RedirectResponse, serve

importlib.reload(bookings)
importlib.reload(expenses)


@app.get("/")
def get_home():
    return RedirectResponse("/bookings")


if __name__ == "__main__":
    serve()
