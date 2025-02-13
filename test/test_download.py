import os
import sqlite3
import tempfile
import pytest
from db.init_db import load_database
from download import download_data


@pytest.fixture
def db():
    db = load_database()
    # Insert test car using dataclass
    Car = db.t.cars.dataclass()
    car = Car(
        id=None,
        name="test car",
        currency="SEK",
        distance_unit="km",
        volume_unit="l",
        car_secret=None,
        fuel_efficiency=0.1,
        cost_per_distance=0.1,
    )
    db.t.cars.insert(car)
    car_id = list(db.t.cars.rows_where("1=1 ORDER BY id DESC LIMIT 1"))[0]["id"]

    # Insert test users using dataclass
    User = db.t.users.dataclass()
    users = ["TestUser1", "TestUser2"]
    for user_name in users:
        user = User(name=user_name, car_id=car_id, password_salt=None)
        db.t.users.insert(user)

    # Insert test expense using dataclass
    Expense = db.t.expenses.dataclass()
    expense = Expense(
        id=None,
        title="Test Expense",
        note="Test Note",
        date="2024-02-13",
        currency="SEK",
        cost=100.0,
        user=users[0],
        type="individual",
        car_id=car_id,
    )
    db.t.expenses.insert(expense)
    expense_id = list(db.t.expenses.rows_where("1=1 ORDER BY id DESC LIMIT 1"))[0]["id"]

    # Insert test booking using dataclass
    Booking = db.t.bookings.dataclass()
    booking = Booking(
        id=None,
        note="Test Booking",
        date_from="2024-02-13",
        date_to="2024-02-14",
        user=users[0],
        distance=100.0,
        expense_id=expense_id,
        car_id=car_id,
    )
    db.t.bookings.insert(booking)

    # Insert test transaction using dataclass
    Transaction = db.t.transactions.dataclass()
    transaction = Transaction(
        id=None,
        date="2024-02-13",
        currency="SEK",
        amount=50.0,
        from_user=users[0],
        to_user=users[1],
    )
    db.t.transactions.insert(transaction)

    yield db

    # Cleanup
    db.conn.execute("delete from transactions")
    db.conn.execute("delete from bookings")
    db.conn.execute("delete from expenses")
    db.conn.execute("delete from users")
    db.conn.execute("delete from cars")


def test_download_data(db):
    # Create a mock session with auth
    mock_sess = {"auth": "TestUser1"}

    # Call download function
    response = download_data(mock_sess)

    # Get the temporary file path from the response
    db_path = response.path

    try:
        # Verify database is valid
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        expected_tables = {
            "cars",
            "users",
            "expenses",
            "bookings",
            "transactions",
            "migrations",
        }
        assert expected_tables.issubset(tables), "Not all expected tables are present"

        # Check migrations table
        cursor.execute("SELECT COUNT(*) FROM migrations")
        assert cursor.fetchone()[0] > 0, "Migrations table should not be empty"

        # Check data in tables
        cursor.execute("SELECT COUNT(*) FROM cars")
        assert cursor.fetchone()[0] == 1, "Cars table should have 1 row"

        cursor.execute("SELECT COUNT(*) FROM users")
        assert cursor.fetchone()[0] == 2, "Users table should have 2 rows"

        cursor.execute("SELECT COUNT(*) FROM expenses")
        assert cursor.fetchone()[0] == 1, "Expenses table should have 1 row"

        cursor.execute("SELECT COUNT(*) FROM bookings")
        assert cursor.fetchone()[0] == 1, "Bookings table should have 1 row"

        cursor.execute("SELECT COUNT(*) FROM transactions")
        assert cursor.fetchone()[0] == 1, "Transactions table should have 1 row"

        # Check specific data
        cursor.execute("SELECT name FROM cars")
        assert cursor.fetchone()[0] == "test car", "Car name doesn't match"

        cursor.execute("SELECT title FROM expenses")
        assert cursor.fetchone()[0] == "Test Expense", "Expense title doesn't match"

        cursor.execute("SELECT amount FROM transactions")
        assert cursor.fetchone()[0] == 50.0, "Transaction amount doesn't match"

        cursor.close()
        conn.close()

    finally:
        # Clean up the temporary file
        if os.path.exists(db_path):
            os.unlink(db_path)
