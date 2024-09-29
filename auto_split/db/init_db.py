from datetime import datetime

from config import DATABASE
from db.migrations import migrations
from fasthtml.common import database

db = None


def load_database():
    global db
    if db is not None:
        return db
    db = database(DATABASE)
    db.conn.execute("PRAGMA foreign_keys = ON;")
    run_db_migrations(db)
    return db


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
