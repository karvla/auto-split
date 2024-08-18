from dotenv import load_dotenv
from app import app, rt
from fasthtml.common import Titled, A, serve, Li, Ul
import bookings
import expenses
import login

load_dotenv()


@rt("/")
def get():
    return Titled(
        "Car pool",
        Ul(
            Li(A("Bookings", href="/bookings")),
            Li(A("Expenses", href="/expenses")),
        ),
    )


if __name__ == "__main__":
    serve()
