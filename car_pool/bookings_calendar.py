from app import app, calendar_path
from bookings import Booking
from config import BASE_URL
from db.init_db import load_database
from fasthtml.common import Response
from ics import Calendar, Event

db = load_database()
bookings = db.t.bookings


@app.get(calendar_path)
def ics_content():
    return Response(
        to_ics_content(bookings()),
        headers={"Content-Disposition": "attachment", "Content-Type": "text/calendar"},
    )


def to_ics_content(bookings: [Booking]) -> str:
    return "\n".join(
        Calendar(
            events=[
                Event(
                    name=f"🚗 {b.user}",
                    description=b.note,
                    begin=b.date_from,
                    end=b.date_to,
                    uid=f"{b.id}@carpoolapp",
                    location=booking_edit_link(b),
                    url=booking_edit_link(b),
                )
                for b in bookings
            ]
        )
    )


def booking_edit_link(b: Booking):
    return f"{BASE_URL}/bookings/edit/{b.id}"
