from app import app
from datetime import datetime
from db.init_db import load_database, run_db_migrations
from fasthtml.common import *
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
import tempfile
import os

db = load_database()


@app.get("/download-data")
def download_data(sess):
    if not sess.get("auth"):
        return RedirectResponse("/login", status_code=303)

    user = db.t.users.get(sess["auth"])
    car_id = user.car_id

    # Create a temporary database file
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    # Create new database and set up schema
    new_db = database(path)
    new_db.conn.execute("PRAGMA foreign_keys = ON;")
    run_db_migrations(new_db)

    # Run migrations on the new database to set up schema
    run_db_migrations(new_db)

    # Copy user data
    # First the car
    car_rows = list(db.t.cars.rows_where("id = ?", [car_id]))
    for row in car_rows:
        new_db.t.cars.insert(db.t.cars.dataclass()(**row))

    # Get all users associated with the car
    user_rows = list(db.t.users.rows_where("car_id = ?", [car_id]))
    user_names = set()
    for row in user_rows:
        new_db.t.users.insert(db.t.users.dataclass()(**row))
        user_names.add(row["name"])

    # Copy expenses for this car
    expense_rows = list(db.t.expenses.rows_where("car_id = ?", [car_id]))
    expense_ids = set()
    for row in expense_rows:
        if row["user"] in user_names:  # Only if the user was copied
            new_db.t.expenses.insert(db.t.expenses.dataclass()(**row))
            expense_ids.add(row["id"])

    # Copy bookings that reference copied expenses
    booking_rows = list(db.t.bookings.rows_where("car_id = ?", [car_id]))
    for row in booking_rows:
        if row["expense_id"] in expense_ids and row["user"] in user_names:
            new_db.t.bookings.insert(db.t.bookings.dataclass()(**row))

    # Copy transactions between copied users
    for user_name in user_names:
        # Get transactions where this user is involved
        from_rows = list(db.t.transactions.rows_where("from_user = ?", [user_name]))
        to_rows = list(db.t.transactions.rows_where("to_user = ?", [user_name]))

        for row in from_rows + to_rows:
            # Only copy if both users are in our exported set
            if row["from_user"] in user_names and row["to_user"] in user_names:
                # Avoid duplicates
                if not list(new_db.t.transactions.rows_where("id = ?", [row["id"]])):
                    new_db.t.transactions.insert(db.t.transactions.dataclass()(**row))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return FileResponse(
        path=path,
        filename=f"car_data_{car_id}_{timestamp}.db",
        media_type="application/octet-stream",
        background=BackgroundTask(lambda: os.unlink(path)),
    )
