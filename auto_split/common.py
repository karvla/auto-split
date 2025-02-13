from dataclasses import fields

from db.init_db import load_database

db = load_database()
users = db.t.users
cars = db.t.cars
User = users.dataclass()
Car = cars.dataclass()


def connected_users(user: str):
    return list(
        map(
            lambda x: next(iter(x.values())),
            db.query(
                """
            select name
            from users
            where car_id = (
                select car_id
                from users
                where name = ?
                limit 1
            )
            """,
                [user],
            ),
        )
    )


def db_fields(db_dataclass, table_name):
    return ", ".join((f"{table_name}.{f.name}" for f in fields(db_dataclass)))


def get_car(user: str):
    car, *_ = db.query(
        f"""
    select {db_fields(Car, "cars")}
    from cars
    where id = (select car_id
            from  users
            where name = ?
            limit 1)
                            """,
        [user],
    )
    return Car(**car)
