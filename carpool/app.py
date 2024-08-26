from fasthtml.common import (
    fast_app,
    Beforeware,
    RedirectResponse,
    Main,
    Nav,
    H1,
    Ul,
    Title,
    Li,
    A,
)
import os


def Page(title: str, *c):
    pages = [
        ("Bookings", "/bookings"),
        ("Expenses", "/expenses"),
    ]
    title = (f"Car pool - {title}",)
    nav_links = [
        Li(A(t, href=l, cls="contrast" + " outline" if t == title else ""))
        for t, l in pages
    ]
    return (
        Title(title),
        Main(
            Nav(Ul(Li(H1(title))), Ul(*nav_links)),
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
app, _ = fast_app(live=use_live_reload, before=beforeware)
