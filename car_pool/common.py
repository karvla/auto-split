from db.init_db import load_database

db = load_database()
users = db.t.users
User = users.dataclass()


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
