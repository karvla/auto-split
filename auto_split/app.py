from config import DEBUG
from db.init_db import load_database
from fasthtml.common import *

db = load_database()


def before(req, sess):
    non_auth = ["/login", "/signup", "/calendar"]
    if any(req.url.path.startswith(p) for p in non_auth):
        return

    auth = req.scope["auth"] = sess.get("auth", None)
    if not auth:
        return RedirectResponse("/login", status_code=303)

    if req.url.path == "/config/new":
        return
    if db.t.users.get(auth).car_id is None:
        return RedirectResponse("/signup/join-or-create", status_code=303)


beforeware = Beforeware(before)
app, _ = fast_app(
    live=DEBUG,
    before=beforeware,
    hdrs=(Script(src="https://unpkg.com/hyperscript.org@0.9.12"),),
)
