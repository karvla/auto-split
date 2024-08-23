from dotenv import load_dotenv

load_dotenv()

from app import app, rt
from fasthtml.common import serve, RedirectResponse
import bookings
import expenses
import login
import bookings_calendar


@rt("/")
def get():
    return RedirectResponse("/bookings")


if __name__ == "__main__":
    serve()
