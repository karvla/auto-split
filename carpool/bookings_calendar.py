from app import app, calendar_path
from bookings import Booking
from db.init_db import db
from fasthtml.common import Response
from datetime import datetime

bookings = db.t.bookings


@app.get(calendar_path)
def ics_content():
    return Response(
        to_ics_content(bookings()),
        headers={"Content-Disposition": "attachment", "Content-Type": "text/calendar"},
    )


def to_ics_content(bookings: [Booking]) -> str:
    def format_datetime(dt):
        if type(dt) is str:
            dt = datetime.fromisoformat(dt)
        return dt.strftime("%Y%m%dT%H%M%S")

    return "\n".join(
        [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Car pool//bookings//EN",
            "ORGANIZER;CN=John Doe:MAILTO:john.doe@example.com",
            *[
                "\n".join(
                    [
                        "BEGIN:VEVENT",
                        "UID:uid1@example.com",
                        f"SUMMARY:{b.user} {b.note}",
                        f"DTSTART:{format_datetime(b.date_from)}",
                        f"DTEND:{format_datetime(b.date_to)}",
                        "LOCATION:",
                        f"DESCRIPTION:{b.note}",
                        "END:VEVENT",
                    ]
                )
                for b in bookings
            ],
            "END:VCALENDAR",
        ]
    )
