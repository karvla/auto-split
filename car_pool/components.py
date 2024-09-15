from fasthtml.common import *


def Icon(svg):
    return Div(svg, style="width: 0.8em; display: inline-block")


def Page(title: str, *c, **kwargs):
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
            **kwargs,
            cls="container",
        ),
    )
