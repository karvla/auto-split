from fasthtml.common import *
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()

app, rt = fast_app(live=True)
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


@rt("/")
def get():
    return Div(
        H1("Car pool"),
        Button("New booking", hx_get="/bookings/add", hx_target="body"),
        bookings_table(),
        #    calendar()
    )


@rt("/bookings/add")
def get(error_msg=""):
    return Div(
        Form(
            booking_form(Booking(), error_msg=""),
            hx_target="this",
            hx_swap="outerHTML",
            hx_post="/bookings/add",
            hx_push_url="/",
        ),
        Div(error_msg),
    )


@rt("/bookings/edit/{id}")
def get(id: int, error_msg=""):
    return Div(
        Form(
            booking_form(bookings[id], error_msg),
            hx_target="this",
            hx_swap="outerHTML",
            hx_post=f"/bookings/edit/{id}",
            hx_push_url="/",
        ),
        Div(error_msg),
    )


@app.post("/bookings/add")
def add_new_booking(booking: Booking):
    if not booking.date_from or not booking.date_to:
        return booking_form(booking, error_msg="Pls add from/to date")
    bookings.insert(booking)
    return RedirectResponse("/", status_code=303)


@app.post("/bookings/edit/{id}")
def edit_booking(booking: Booking, id: int):
    if not booking.date_from or not booking.date_to:
        return booking_form(booking, error_msg="Pls add from/to date")
    bookings.update(booking)
    return RedirectResponse("/", status_code=303)


@app.delete("/bookings/{id}")
def delete_booking(id: int):
    bookings.delete(id)
    return RedirectResponse("/", status_code=303)


def booking_form(booking: Booking, error_msg=""):
    return Group(
        Select(*[Option(u.name) for u in users()], name="user"),
        Input(type="text", name="id", value=booking.id, style="display:none"),
        Input(type="date", name="date_from", value=booking.date_from),
        Input(type="date", name="date_to", value=booking.date_to),
        Input(type="text", name="note", placeholder="note", value=booking.note),
        Button("Update" if booking.id else "Add"),
        Div(error_msg),
        style="flex-direction: column",
    )


def bookings_table():
    return Table(
        Tr(Th("Note"), Th("From"), Th("To"), Th("User"), Th(), Th()),
        *[
            Tr(
                Td(b.note),
                Td(b.date_from),
                Td(b.date_to),
                Td(b.user),
                Td(A("Edit", href=f"/bookings/edit/{b.id}")),
                Td(
                    Button(
                        "Delete",
                        hx_delete=f"/bookings/{b.id}",
                        hx_confirm="Are you sure you want to delete this booking?",
                        hx_swap="delete",
                        hx_target="closest tr",
                    )
                ),
            )
            for b in bookings()
        ],
    )


# def calendar(): return Iframe(src=f'https://calendar.google.com/calendar/embed?src={get_calendar_id()}&ctz=Europe%2FStockholm', width="100%", height="600")

# def get_calendar_id():
#    return GoogleCalendar(credentials=credentials).get_calendar().calendar_id


# def update_calendar():
#    gc = GoogleCalendar(credentials=credentials)
#    events = list(gc.get_events())
#
#    start = date(2024,8,1)
#    end = date(2024,8,2)
#    event = Event('Vacation',
#                  visibility="public",
#              start=start,
#              end=end)
#    gc.add_event(event)
#    print(events)
#    for event in gc.get_events():
#        print(event)
#


# update_calendar()


serve()
