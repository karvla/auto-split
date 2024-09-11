import os

import pytest
from db.init_db import load_database, run_db_migrations


@pytest.fixture(autouse=True)
def db():
    os.environ["USERS"] = "user1,user2,user3"
    os.environ["CURRENCY"] = "USD"
    os.environ["FUEL_EFFICIENCY"] = "0.1"
    os.environ["COST_PER_DISTANCE"] = "0.5"
    os.environ["DISTANCE_UNIT"] = "km"
    os.environ["VOLUME_UNIT"] = "liters"
    db = load_database(test=True)
    run_db_migrations(db)
    yield db

    for table in db.table_names():
        db[table].drop()
