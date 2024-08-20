from app import rt, app, bookings, Booking, users, Page
from fasthtml.common import (
    Response,
    Titled,
    Div,
    Form,
    Group,
    A,
    Table,
    Tr,
    Td,
    Th,
    Button,
    Input,
    Label,
    Select,
    Option,
)


@rt("/bookings")
def get():
    return bookings_table()


@rt("/bookings/add")
def get():
    return booking_form(
        Booking(id=None, date_from=None, date_to=None, user=None, note=None),
        "Add booking",
        "/bookings/add",
    )


@rt("/bookings/edit/{id}")
def get(id: int):
    return (booking_form(bookings[id], "Edit booking", "/bookings/edit"),)


@app.post("/bookings/add")
def add_new_booking(booking: Booking):
    is_valid, msg = validate_booking(booking)
    booking.id = None
    if not is_valid:
        return msg
    bookings.insert(booking)
    return Response(headers={"HX-Location": "/bookings"})


@app.post("/bookings/edit")
def edit_booking(booking: Booking, id: int):
    is_valid, msg = validate_booking(booking)
    if not is_valid:
        return booking_form(booking, "Edit booking", "/bookings/edit")
    bookings.update(booking)
    return Response(headers={"HX-Location": "/bookings"})


@app.post("/bookings/validate")
def edit_booking(booking: Booking):
    is_valid, msg = validate_booking(booking)
    if not is_valid:
        return msg


@app.delete("/bookings/{id}")
def delete_booking(id: int):
    bookings.delete(id)
    return Response(headers={"HX-Location": "/bookings"})


@app.post("/bookings/validate")
def validate_booking(booking: Booking) -> (bool, str | None):
    if not booking.date_from or not booking.date_to:
        return False, "Pls add booking duration"
    if booking.date_from > booking.date_to:
        return False, "Start time should be before end time"
    for b in bookings(where=f"id != {booking.id}"):
        if (
            b.date_from < booking.date_from < b.date_to
            or b.date_from < booking.date_to < b.date_to
            or booking.date_from < b.date_to < booking.date_to
            or booking.date_from < b.date_from < booking.date_to
        ):
            return False, "There's already a booking for this time span"
    return True, None


def booking_form(booking: Booking, title, post_target):
    return Page(
        title,
        Form(
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
            Div(id="indicator"),
            Button("Save"),
            hx_post=post_target,
            hx_target="#indicator",
            style="flex-direction: column",
        ),
    )


def bookings_table():
    return Page(
        "Bookings",
        A("New booking", href="/bookings/add"),
        Div(
            Table(
                Tr(Th("When"), Th("Note"), Th("User"), Th(), Th()),
                *[
                    Tr(
                        Td(f"{b.date_from} {b.date_to}"),
                        Td(b.note),
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
                cls="striped",
            ),
            cls="overflow-auto",
        ),
    )
