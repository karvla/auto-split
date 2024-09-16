from datetime import datetime, timedelta

from bookings import (
    Booking,
    add_new_booking,
    delete_booking,
    edit_booking,
    validate_booking,
)
from test_db import db


def test_users_table(db):
    users = db.t.users
    assert users.exists()


def test_add_new_booking(db):
    bookings = db.t.bookings

    new_booking = Booking(
        id=None,
        expense_id=None,
        date_from=(datetime.now() + timedelta(days=1)).date().isoformat(),
        date_to=(datetime.now() + timedelta(days=2)).date().isoformat(),
        user="user1",
        note="Test booking",
        distance=100,
    )

    add_new_booking(new_booking)
    assert len(bookings()) == 1


def test_edit_booking(db):
    bookings = db.t.bookings

    new_booking = Booking(
        id=None,
        expense_id=None,
        date_from=(datetime.now() + timedelta(days=1)).date().isoformat(),
        date_to=(datetime.now() + timedelta(days=2)).date().isoformat(),
        user="user1",
        note="Test booking",
        distance=100,
        car_id=1,
    )

    add_new_booking(new_booking)
    booking = bookings()[0]
    booking.note = "Updated booking"

    response = edit_booking(booking)
    assert response.headers["HX-Location"] == "/bookings"
    assert bookings[booking.id].note == "Updated booking"


def test_validate_booking(db):
    bookings = db.t.bookings

    new_booking = Booking(
        id=None,
        expense_id=None,
        date_from=(datetime.now() + timedelta(days=1)).date().isoformat(),
        date_to=(datetime.now() + timedelta(days=2)).date().isoformat(),
        user="user1",
        note="Test booking",
        distance=100,
    )

    is_valid, msg = validate_booking(new_booking)
    assert is_valid

    add_new_booking(new_booking)

    is_valid, msg = validate_booking(new_booking)
    assert not is_valid
    assert msg == "There's already a booking for this time span"


def test_delete_booking(db):
    bookings = db.t.bookings

    new_booking = Booking(
        id=None,
        expense_id=None,
        date_from=(datetime.now() + timedelta(days=1)).isoformat(),
        date_to=(datetime.now() + timedelta(days=2)).isoformat(),
        user="user1",
        note="Test booking",
        distance=100,
    )

    add_new_booking(new_booking)
    booking = bookings()[0]

    response = delete_booking(booking.id)
    assert response.headers["HX-Location"] == "/bookings"
    assert len(bookings()) == 0
