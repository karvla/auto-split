from db.expense_type import ExpenseType


def init_migration(db):
    users = db.t.users
    if users not in db.t:
        users.create(name=str, pk="name")

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
    users.add_column("password_salt", col_type="str")


def add_cars_table(db):
    cars = db.t.cars
    cars.create(id=int, name=str, car_secret=str, pk="id")

    db.t.users.add_column("car_id", col_type=int)
    db.t.bookings.add_column("car_id", col_type=int)
    db.t.expenses.add_column("car_id", col_type=int)

    db.t.users.add_foreign_key("car_id", "cars", "id")
    db.t.bookings.add_foreign_key("car_id", "cars", "id")
    db.t.expenses.add_foreign_key("car_id", "cars", "id")


def move_config_to_cars_table(db):
    cars = db.t.cars
    cars.add_column("currency", col_type=str)
    cars.add_column("distance_unit", col_type=str)
    cars.add_column("volume_unit", col_type=str)
    cars.add_column("fuel_efficiency", col_type=float)
    cars.add_column("cost_per_distance", col_type=float)


migrations = [
    init_migration,
    add_expense_type,
    add_user_id,
    add_transaction_table,
    add_user_password,
    add_cars_table,
    move_config_to_cars_table,
]
