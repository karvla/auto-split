from dotenv import load_dotenv
from app import app, rt
from fasthtml.common import serve, RedirectResponse
import bookings
import expenses
import login

load_dotenv()


@rt("/")
def get():
    return RedirectResponse("/bookings")


if __name__ == "__main__":
    serve()
