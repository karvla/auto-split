import os
from datetime import datetime
from fasthtml.common import database

db = database("data/carpool.db")


def init_migration():

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


migrations = [
    init_migration,
]


def run_db_migrations():
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
            migration()
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