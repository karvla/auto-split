from datetime import datetime, timedelta

import costs
from bookings import (
    Booking,
    add_new_booking,
    delete_booking,
    edit_booking,
    get_ride_cost,
    resolved_gas_price,
    validate_booking,
)
from expenses import expenses
from test_db import db


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
        car_id=1,
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
        car_id=1,
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
        car_id=1,
    )

    add_new_booking(new_booking)
    booking = bookings()[0]

    response = delete_booking(booking.id)
    assert response.headers["HX-Location"] == "/bookings"
    assert len(bookings()) == 0


def test_gas_price_is_stored_and_overridable(db):
    db.t.cars.update(id=1, fuel_efficiency=0.1, cost_per_distance=0.2)
    sess = {"auth": "User0"}

    new_booking = Booking(
        id=None,
        expense_id=None,
        date_from=(datetime.now() + timedelta(days=1)).date().isoformat(),
        date_to=(datetime.now() + timedelta(days=2)).date().isoformat(),
        user="User0",
        note="Test booking",
        distance=100,
        gas_price=20.0,
        car_id=1,
    )
    add_new_booking(new_booking, sess)

    booking = db.t.bookings()[0]
    assert booking.gas_price == 20.0
    assert expenses[booking.expense_id].cost == 100 * (20.0 * 0.1 + 0.2)

    booking.gas_price = 15.0
    edit_booking(booking, sess)

    assert db.t.bookings[booking.id].gas_price == 15.0
    assert expenses[booking.expense_id].cost == 100 * (15.0 * 0.1 + 0.2)


def test_ride_cost_falls_back_to_current_gas_price(db, monkeypatch):
    db.t.cars.update(id=1, fuel_efficiency=0.1, cost_per_distance=0.2)
    monkeypatch.setattr(costs, "get_gas_price", lambda: 10.0)

    assert get_ride_cost(100, None, {"auth": "User0"}) == 100 * (10.0 * 0.1 + 0.2)


def test_resolved_gas_price(monkeypatch):
    monkeypatch.setattr(costs, "get_gas_price", lambda: 10.0)
    assert resolved_gas_price(20.5) == 20.5
    assert resolved_gas_price("20.5") == 20.5
    assert resolved_gas_price(None) == 10.0
    assert resolved_gas_price("") == 10.0

    # A failed scrape returns None, which must not blow up the cost formula
    monkeypatch.setattr(costs, "get_gas_price", lambda: None)
    assert resolved_gas_price(None) == 0
