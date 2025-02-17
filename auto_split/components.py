from fasthtml.common import *
from fa6_icons import svgs


def Icon(svg):
    return Div(svg, style="width: 0.8em; display: inline-block")


def Page(current_title: str, *c, **kwargs):
    pages = [
        ("Bookings", "/bookings"),
        ("Expenses", "/expenses"),
        ("Debts", "/debts"),
        (Icon(svgs.gear.solid), "/config/edit"),
    ]
    nav_links = [
        Li(
            A(
                page_title,
                href=link,
                cls="contrast" + " outline" if page_title == page_title else "",
            )
        )
        for page_title, link in pages
    ]
    title = f"🚗 {current_title} "
    return (
        Title(title),
        Main(
            Nav(Ul(Li(H3("🚗"))), Ul(*nav_links)),
            *c,
            **kwargs,
            cls="container",
        ),
    )
