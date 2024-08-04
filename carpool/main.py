from fasthtml.common import (
    fast_app,
    database,
    Beforeware,
    RedirectResponse,
    Response,
    serve,
    Div,
    Form,
    Group,
    Titled,
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
from dataclasses import dataclass
from dotenv import load_dotenv
from datetime import datetime
import os
from app import app, rt, db, Booking, User, bookings, users
import login

load_dotenv()



@rt("/")
def get():
    return Titled(
        "Car pool",
        A("New booking", href="/bookings/add"),
        bookings_table(),
    )


@rt("/bookings/add")
def get(error_msg=""):
    return booking_form(Booking(), "/bookings/add")


@rt("/bookings/edit/{id}")
def get(id: int):
    return (booking_form(bookings[id], "/bookings/edit"),)


@app.post("/bookings/add")
def add_new_booking(booking: Booking):
    is_valid, msg = validate_booking(booking)
    booking.id = None
    if not is_valid:
        return msg
    bookings.insert(booking)
    return Response(headers={"HX-Location": "/"})


@app.post("/bookings/edit")
def edit_booking(booking: Booking, id: int):
    is_valid, msg = validate_booking(booking)
    if not is_valid:
        return booking_form(booking, "/bookings/edit")
    bookings.update(booking)
    return Response(headers={"HX-Location": "/"})


@app.post("/bookings/validate")
def edit_booking(booking: Booking):
    is_valid, msg = validate_booking(booking)
    if not is_valid:
        return msg


@app.delete("/bookings/{id}")
def delete_booking(id: int):
    bookings.delete(id)
    return Response(headers={"HX-Location": "/"})


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


def booking_form(booking: Booking, post_target):
    return Form(
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
        Button("Add" if booking.id is None else "Update"),
        hx_post=post_target,
        hx_target="#indicator",
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

if __name__ == "__main__":
    serve()