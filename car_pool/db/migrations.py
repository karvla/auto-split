from auth import hash_password
from config import (
    ADMIN_PASSWORD,
    ADMIN_USERNAME,
    CALENDAR_SECRET,
    COST_PER_DISTANCE,
    CURRENCY,
    DISTANCE_UNIT,
    FUEL_EFFICIENCY,
    USERS,
    VOLUME_UNIT,
)
from db.expense_type import ExpenseType


def init_migration(db):
    users = db.t.users
    if users not in db.t:
        users.create(name=str, pk="name")
        for user in USERS:
            users.insert(name=user)

    expenses = db.t.expenses
    if expenses not in db.t:
        expenses.create(
            id=int,
            title=str,
            note=str,
            date=str,
            currency=str,
            cost=float,
            user=str,
            pk="id",
        )

    bookings = db.t.bookings
    if bookings not in db.t:
        bookings.create(
            id=int,
            note=str,
            date_from=str,
            date_to=str,
            user=str,
            pk="id",
            distance=float,
            expense_id=int,
        )
        bookings.add_foreign_key("expense_id", "expenses", "id")


def add_expense_type(db):
    expenses = db.t.expenses
    expenses.add_column("type", col_type=str, not_null_default=ExpenseType.individual)


def add_user_id(db):
    users = db.t.users
    users.transform(pk="name")


def add_transaction_table(db):
    transactions = db.t.transactions
    transactions.create(
        id=int,
        date=str,
        currency=str,
        amount=float,
        from_user=str,
        to_user=str,
        pk="id",
    )
    transactions.add_foreign_key("from_user", "users", "name")
    transactions.add_foreign_key("to_user", "users", "name")


def add_user_password(db):
    users = db.t.users
    users.insert({"name": ADMIN_USERNAME})
    users.add_column("password_salt", col_type="str")

    # All users are given the admin password
    # since they have all used this to sign in at
    # this point
    for user in users.rows:
        user["password_salt"] = hash_password(ADMIN_PASSWORD)
        users.upsert(user)


def add_cars_table(db):
    cars = db.t.cars
    cars.create(id=int, name=str, calendar_secret=str, pk="id")
    init_car = cars.insert({"name": "Initial car", "calendar_secret": CALENDAR_SECRET})
    db.t.users.add_column("car_id", int)
    db.t.users.add_foreign_key("car_id", "cars", "id")
    db.execute("UPDATE users SET car_id = ?", [init_car["id"]])

    db.t.bookings.add_column("car_id", col_type=int, not_null_default=init_car["id"])
    db.t.bookings.add_foreign_key("car_id", "cars", "id")

    db.t.expenses.add_column("car_id", col_type=int, not_null_default=init_car["id"])
    db.t.expenses.add_foreign_key("car_id", "cars", "id")


def move_config_to_cars_table(db):
    cars = db.t.cars
    cars.add_column("car_secret", col_type=str)
    cars.add_column("currency", col_type=str)
    cars.add_column("distance_unit", col_type=str)
    cars.add_column("volume_unit", col_type=str)
    cars.add_column("fuel_efficiency", col_type=float)
    cars.add_column("cost_per_distance", col_type=float)

    # Update the initial car with the relevant attributes from config
    cars.upsert(
        {
            "id": 1,
            "car_secret": CALENDAR_SECRET,
            "currency": CURRENCY,
            "distance_unit": DISTANCE_UNIT,
            "volume_unit": VOLUME_UNIT,
            "fuel_efficiency": FUEL_EFFICIENCY,
            "cost_per_distance": COST_PER_DISTANCE,
        },
    )


migrations = [
    init_migration,
    add_expense_type,
    add_user_id,
    add_transaction_table,
    add_user_password,
    add_cars_table,
    move_config_to_cars_table,
]
