from config import DEBUG
from fasthtml.common import *


def before(req, sess):
    non_auth = ["/login", "/signup", "/calendar"]
    if any(req.url.path.startswith(p) for p in non_auth):
        return

    auth = req.scope["auth"] = sess.get("auth", None)
    if not auth:
        return RedirectResponse("/login", status_code=303)


beforeware = Beforeware(before)
use_live_reload = DEBUG is not None
app, _ = fast_app(
    live=use_live_reload,
    before=beforeware,
    hdrs=(Script(src="https://unpkg.com/hyperscript.org@0.9.12"),),
)
