from fasthtml.common import (
    fast_app,
    Beforeware,
    RedirectResponse,
    Main,
    Nav,
    H3,
    Ul,
    Title,
    Li,
    Script,
    A,
)
import os


def Page(title: str, *c):
    pages = [
        ("Bookings", "/bookings"),
        ("Expenses", "/expenses"),
        ("Debts", "/debts"),
    ]
    title = (f"🚗 {title}",)
    nav_links = [
        Li(A(t, href=l, cls="contrast" + " outline" if t == title else ""))
        for t, l in pages
    ]
    return (
        Title(title),
        Main(
            Nav(Ul(Li(H3(title))), Ul(*nav_links)),
            *c,
            cls="container",
        ),
    )


def before(req, sess):
    auth = req.scope["auth"] = sess.get("auth", None)
    if not auth:
        return RedirectResponse("/login", status_code=303)


calendar_path = f"/{os.getenv('CALENDAR_SECRET')}.ics"
beforeware = Beforeware(before, skip=["/login", calendar_path])
use_live_reload = os.getenv("DEBUG") is not None
app, _ = fast_app(
    live=use_live_reload,
    before=beforeware,
    hdrs=(Script(src="https://unpkg.com/hyperscript.org@0.9.12"),),
)
