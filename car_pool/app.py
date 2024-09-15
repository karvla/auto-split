from config import CALENDAR_SECRET, DEBUG
from fasthtml.common import *


def before(req, sess):
    auth = req.scope["auth"] = sess.get("auth", None)
    if not auth:
        return RedirectResponse("/login", status_code=303)


calendar_path = f"/{CALENDAR_SECRET}.ics"
beforeware = Beforeware(before, skip=["/login", calendar_path])
use_live_reload = DEBUG is not None
app, _ = fast_app(
    live=use_live_reload,
    before=beforeware,
    hdrs=(Script(src="https://unpkg.com/hyperscript.org@0.9.12"),),
)
