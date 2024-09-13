import os

import pytest
from db.init_db import load_database, run_db_migrations

db = load_database()


@pytest.fixture(autouse=True)
def db():
    db = load_database()
    run_db_migrations(db)
    yield db

    for table in db.table_names():
        db[table].drop()
