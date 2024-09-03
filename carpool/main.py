from dotenv import load_dotenv
from db.init_db import run_db_migrations

load_dotenv()
run_db_migrations()
from app import app
from fasthtml.common import serve, RedirectResponse
import importlib
import bookings
import expenses
import login
import bookings_calendar
import debts

importlib.reload(bookings)
importlib.reload(expenses)


@app.get("/")
def get_home():
    return RedirectResponse("/bookings")


if __name__ == "__main__":
    serve()
