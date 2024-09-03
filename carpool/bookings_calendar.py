from app import app, calendar_path
from bookings import Booking
from db.init_db import db
import os
from fasthtml.common import Response
from datetime import datetime, timedelta
from bookings import booking_time_range

bookings = db.t.bookings


@app.get(calendar_path)
def ics_content():
    return Response(
        to_ics_content(bookings()),
        headers={"Content-Disposition": "attachment", "Content-Type": "text/calendar"},
    )


def to_ics_content(bookings: [Booking]) -> str:
    def format_datetime(dt):
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
                        f"SUMMARY:🚗 {b.user} - {b.note} ",
                        f"DTSTART:{format_datetime(booking_time_range(b)[0])}",
                        f"DTEND:{format_datetime(booking_time_range(b)[1] + timedelta(1))}",
                        f"LOCATION:{booking_edit_link(b)}",
                        f"DESCRIPTION:{booking_summary(b)}",
                        "END:VEVENT",
                    ]
                )
                for b in bookings
            ],
            "END:VCALENDAR",
        ]
    )


def booking_summary(b: Booking):
    return "\n".join(
        [
            booking_edit_link(b),
            b.note,
        ]
    )


def booking_edit_link(b: Booking):
    return f"{os.getenv('BASE_URL')}/bookings/edit/{b.id}"
