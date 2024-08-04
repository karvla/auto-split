from fasthtml.common import (
    fast_app,
    database,
    Beforeware,
    RedirectResponse,
    Response,
    serve,
    Div,
    Form,
    Group,
    Titled,
    A,
    Table,
    Tr,
    Td,
    Th,
    Button,
    Input,
    Label,
    Select,
    Option,
)
from datetime import datetime
import os


def before(req, sess):
    auth = req.scope["auth"] = sess.get("auth", None)
    if not auth:
        return RedirectResponse("/login", status_code=303)


beforeware = Beforeware(before, skip=["/login"])
use_live_reload = os.getenv("DEBUG") is not None
app, rt = fast_app(live=use_live_reload, before=beforeware)

db = database("data/carpool.db")
users, bookings = db.t.users, db.t.bookings
if users not in db.t:
    users.create(name=str, pk="name")
    for user in os.getenv("USERS").split(","):
        users.insert(name=user)

    bookings.create(
        id=int, note=str, date_from=datetime, date_to=datetime, user=str, pk="id"
    )
Booking, User = bookings.dataclass(), users.dataclass()


