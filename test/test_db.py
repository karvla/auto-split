import os

import pytest
from db.init_db import load_database, run_db_migrations

db = load_database()


@pytest.fixture(autouse=True)
def db():
    db = load_database()
    yield db

    db.conn.execute("delete from bookings")
    db.conn.execute("delete from expenses")
    db.conn.execute("delete from transactions")
