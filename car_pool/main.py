import bookings
import bookings_calendar
import debts
import expenses
import login
from app import app
from db.init_db import load_database
from fasthtml.common import RedirectResponse, serve


@app.get("/")
def get_home():
    return RedirectResponse("/bookings")


if __name__ == "__main__":
    load_database()
    serve()
