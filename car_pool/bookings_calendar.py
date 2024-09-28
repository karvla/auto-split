from app import app
from config import BASE_URL
from db.init_db import load_database
from fasthtml.common import Response
from ics import Calendar, Event

db = load_database()
bookings = db.t.bookings
cars = db.t.cars
Car = cars.dataclass()
Booking = bookings.dataclass()


def calendar_secret(sess=None):
    if sess is None:
        return None
    secret = db.query(
        """
        select calendar_secret
        from cars
        where cars.id = (select car_id
                        from users
                        where users.name = ?
                        limit 1)
                 """,
        [sess["auth"]],
    )
    return next(iter(secret))["calendar_secret"]


@app.get("/calendar/{calendar_path}")
def ics_content(calendar_path: str):
    calendar_secret, _ = calendar_path.split(".")
    c = cars(where="calendar_secret = ?", where_args=[calendar_secret], limit=1)
    if len(c) == 0:
        return Response(status_code=404)

    return Response(
        to_ics_content(bookings(where="car_id = ?", where_args=[c[0].id])),
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
