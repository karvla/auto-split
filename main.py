from fasthtml.common import *
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()

app, rt = fast_app(live=os.getenv("DEBUG") is not None)
db = database("data/carpool.db")

users, bookings = db.t.users, db.t.bookings
if users not in db.t:
    users.create(name=str, pk="name")
    for user in os.getenv("USERS").split(","):
        users.insert(name=user)

    bookings.create(
        id=int, note=str, date_from=datetime, date_to=datetime, user=str, pk="id"
    )
Booking, User = bookings.dataclass(), users.dataclass()


@rt("/")
def get():
    return Div(
        H1("Car pool"),
        A("New booking", href="/bookings/add"),
        bookings_table(),
    )


@rt("/bookings/add")
def get(error_msg=""):
    return Div(
        Form(
            booking_form(Booking()),
            hx_target="this",
            hx_swap="outerHTML",
            hx_post="/bookings/add",
        ),
    )


@rt("/bookings/edit/{id}")
def get(id: int):
    return Div(
        Form(
            booking_form(bookings[id]),
            hx_target="this",
            hx_swap="outerHTML",
            hx_post=f"/bookings/edit/{id}",
        ),
    )


@app.post("/bookings/add")
def add_new_booking(booking: Booking):
    is_valid, msg = validate_booking(booking)
    if not is_valid:
        return booking_form(booking, error_msg=msg)
    bookings.insert(booking)
    return RedirectResponse("/", status_code=303)


@app.post("/bookings/edit/{id}")
def edit_booking(booking: Booking, id: int):
    is_valid, msg = validate_booking(booking)
    if not is_valid:
        return booking_form(booking, error_msg=msg)
    bookings.update(booking)
    return RedirectResponse("/", status_code=303)


@app.delete("/bookings/{id}")
def delete_booking(id: int):
    bookings.delete(id)
    return RedirectResponse("/", status_code=303)


def validate_booking(booking: Booking) -> (bool, Optional[str]):
    if not booking.date_from or not booking.date_to:
        return False, "Pls add booking duration"
    if booking.date_from > booking.date_to:
        return False, "Start time should be before end time"
    print(booking)
    for b in bookings(where=f"id != {booking.id}"):
        if (
            b.date_from < booking.date_from < b.date_to
            or b.date_from < booking.date_to < b.date_to
            or booking.date_from < b.date_to < booking.date_to
            or booking.date_from < b.date_from < booking.date_to
        ):
            return False, "There's already a booking for this time span"
    return True, None


def booking_form(booking: Booking, error_msg=""):
    return Group(
        Group(
            Div(
                Label("From", _for="date_from"),
                Input(type="date", name="date_from", value=booking.date_from),
            ),
            Div(
                Label("To", _for="date_to"),
                Input(type="date", name="date_to", value=booking.date_to),
            ),
            style="flex-direction: row",
        ),
        Select(*[Option(u.name) for u in users()], name="user"),
        Input(type="text", name="id", value=booking.id, style="display:none"),
        Input(type="text", name="note", placeholder="note", value=booking.note),
        Button("Add" if booking.id is None else "Update"),
        Div(error_msg),
        style="flex-direction: column",
    )


def bookings_table():
    return Table(
        Tr(Th("Note"), Th("From"), Th("To"), Th("User"), Th(), Th()),
        *[
            Tr(
                Td(b.note),
                Td(b.date_from),
                Td(b.date_to),
                Td(b.user),
                Td(A("Edit", href=f"/bookings/edit/{b.id}")),
                Td(
                    Button(
                        "Delete",
                        hx_delete=f"/bookings/{b.id}",
                        hx_confirm="Are you sure you want to delete this booking?",
                        hx_swap="delete",
                        hx_target="closest tr",
                    )
                ),
            )
            for b in bookings()
        ],
    )

serve()
