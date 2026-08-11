import pytest
from db.migrations import add_booking_gas_price, gas_price_from_note, migrations
from fastlite import database

NOTE = (
    "This ride costs distance x (gas price x fuel efficiency + fixed cost)\n"
    "= 800.0 km x (16.8 SEK/l x 0.08 l / km + 0.1 SEK/km)\n"
    "= 1155.2 SEK"
)


@pytest.fixture
def old_db():
    """A database migrated up to just before the gas price migration."""
    db = database(":memory:")
    db.conn.execute("PRAGMA foreign_keys = ON;")
    for migration in migrations[: migrations.index(add_booking_gas_price)]:
        migration(db)
    db.t.cars.insert(name="test car", fuel_efficiency=0.08, cost_per_distance=0.1)
    db.t.users.insert(name="User0", car_id=1)
    yield db


def insert_booking(db, distance, cost, note):
    expense = db.t.expenses.insert(
        title="Ride cost",
        date="2024-01-01",
        user="User0",
        cost=cost,
        note=note,
        car_id=1,
    )
    return db.t.bookings.insert(
        note="a ride",
        date_from="2024-01-01",
        date_to="2024-01-02",
        user="User0",
        distance=distance,
        expense_id=expense["id"],
        car_id=1,
    )


def test_reads_the_gas_price_from_the_expense_note():
    assert gas_price_from_note(NOTE) == 16.8
    assert gas_price_from_note("nothing to see here") is None
    assert gas_price_from_note(None) is None


def test_backfills_the_gas_price_from_the_note(old_db):
    booking = insert_booking(old_db, distance=800, cost=1155.2, note=NOTE)

    add_booking_gas_price(old_db)

    assert old_db.t.bookings.get(booking["id"])["gas_price"] == 16.8


def test_leaves_gas_price_null_when_the_note_has_no_price(old_db):
    no_note = insert_booking(old_db, distance=100, cost=144.4, note=None)
    other_note = insert_booking(old_db, distance=100, cost=144.4, note="hand written")

    add_booking_gas_price(old_db)

    assert old_db.t.bookings.get(no_note["id"])["gas_price"] is None
    assert old_db.t.bookings.get(other_note["id"])["gas_price"] is None
