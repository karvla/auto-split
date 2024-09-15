import os
from datetime import datetime

from auth import hash_password
from config import ADMIN_PASSWORD, ADMIN_USERNAME, DATABASE
from db.expense_type import ExpenseType
from dotenv import load_dotenv
from fasthtml.common import database

db = None


def load_database():
    global db
    if db is not None:
        return db
    db = database(DATABASE)
    run_db_migrations(db)
    return db


def init_migration(db):
    load_dotenv()
    users = db.t.users
    if users not in db.t:
        users.create(name=str, pk="name")
        for user in os.getenv("USERS").split(","):
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


migrations = [
    init_migration,
    add_expense_type,
    add_user_id,
    add_transaction_table,
    add_user_password,
]


def run_db_migrations(db):
    migrations_table = db.t.migrations
    if migrations_table not in db.t:
        migrations_table.create(
            id=int, title=str, message=str, success=bool, date=str, pk="id"
        )
    Migration = migrations_table.dataclass()

    for id, migration in enumerate(migrations):
        if id in migrations_table:
            continue
        title = migration.__str__().split(" ")[1]
        date = datetime.utcnow().ctime()
        print("Running migration", title, end=" ")
        try:
            migration(db)
        except Exception as e:
            print("FAIL:", e)
            migrations_table.insert(
                Migration(id=id, title=title, message=e, success=False, date=date)
            )
            exit()
            continue

        migrations_table.insert(
            Migration(id=id, title=title, message="", success=True, date=date)
        )
        print("OK")
