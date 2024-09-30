import os

import pytest
from db.init_db import load_database, run_db_migrations

db = load_database()

User = db.t.users.dataclass()
Car = db.t.cars.dataclass()


@pytest.fixture(autouse=True)
def db():
    db = load_database()
    db.t.cars.insert(name="test car")
    [db.t.users.insert(User(name=f"User{i}", car_id=1)) for i in range(3)]
    yield db

    db.conn.execute("delete from bookings")
    db.conn.execute("delete from expenses")
    db.conn.execute("delete from transactions")
    db.conn.execute("delete from users")
    db.conn.execute("delete from cars")
