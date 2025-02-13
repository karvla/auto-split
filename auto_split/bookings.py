from datetime import datetime

import costs
from app import app
from bookings_calendar import calendar_secret
from common import connected_users, db_fields, get_car
from components import Icon, Page
from config import BASE_URL
from db.expense_type import ExpenseType
from db.init_db import load_database
from expenses import Expense, expenses
from fa6_icons import svgs
from fasthtml.common import *

db = load_database()
bookings = db.t.bookings
Booking = bookings.dataclass()
users = db.t.users
User = users.dataclass()


def get_bookings(sess):
    return map(
        lambda b: Booking(**b),
        db.query(
            f"""
            select {db_fields(Booking, "bookings")}
            from bookings
            left join users
            on users.car_id = bookings.car_id
            where users.name = ?
            order by date_from desc
                        """,
            [sess["auth"]],
        ),
    )


def has_access(booking: Booking, sess):
    if sess is None:
        return True
    return (
        db.t.users.count_where(
            "name = ? and car_id = ?", [sess["auth"], booking.car_id]
        )
        > 0
    )


@app.get("/bookings/add")
def add_booking_form(sess):
    user_name = sess["auth"]
    user, *_ = db.t.users.rows_where("name = ?", [user_name])
    return booking_form(
        Booking(
            id=None,
            expense_id=None,
            date_from=None,
            date_to=None,
            user=user_name,
            note=None,
            distance=None,
            car_id=user["car_id"],
        ),
        "Add booking",
        "/bookings/add",
        sess,
    )


def booking_expense(booking: Booking, sess=None) -> Expense:
    expense_note = "\n".join(
        [p for p in get_cost_description(booking.distance, sess) if type(p) is str]
    )
    return Expense(
        id=None,
        date=booking.date_from,
        title=f"Ride cost: {booking.note}",
        note=expense_note,
        user=booking.user,
        cost=get_ride_cost(booking.distance, sess),
        currency=get_car(sess["auth"]).currency if sess is not None else "",
        type=ExpenseType.individual,
        car_id=booking.car_id,
    )


@app.post("/bookings/add")
def add_new_booking(booking: Booking, sess=None):
    booking.id = None
    if not has_access(booking, sess):
        return RedirectResponse("/bookings")
    is_valid, msg = validate_booking(booking)
    if not is_valid:
        return msg

    expense = expenses.insert(booking_expense(booking, sess))
    booking.expense_id = expense.id
    bookings.insert(booking)
    return Response(headers={"HX-Location": "/bookings"})


@app.get("/bookings/edit/{id}")
def edit_existing_booking(id: int, sess=None):
    booking = bookings[id]
    if not has_access(booking, sess):
        return RedirectResponse("/bookings")

    return booking_form(booking, "Edit booking", "/bookings/edit", sess)


@app.post("/bookings/edit")
def edit_booking(booking: Booking, sess=None):
    if not has_access(booking, sess):
        return RedirectResponse("/bookings")
    is_valid, msg = validate_booking(booking)
    if not is_valid:
        return msg
    bookings.update(booking)
    updated_expense = booking_expense(booking, sess)
    updated_expense.id = booking.expense_id
    expenses.upsert(updated_expense)
    return Response(headers={"HX-Location": "/bookings"})


@app.post("/bookings/validate")
def validate(booking: Booking, sess=None):
    if not has_access(booking, sess):
        return RedirectResponse("/bookings")
    is_valid, msg = validate_booking(booking)
    if not is_valid:
        return msg


@app.delete("/bookings/{id}")
def delete_booking(id: int, sess=None):
    booking = bookings[id]
    if not has_access(booking, sess):
        return Response(status_code=401)

    bookings.delete(id)
    expenses.delete_where(where="id == ?", where_args=[booking.expense_id])
    return Response(headers={"HX-Location": "/bookings"})


@app.post("/bookings/validate")
def validate_booking(booking: Booking) -> (bool, str | None):
    date_from, date_to = booking_time_range(booking)

    if not date_from or not date_to:
        return False, "Please add a valid booking duration"

    if date_from > date_to:
        return False, "Start time should be before end time"

    for other_booking in bookings(where="car_id = ?", where_args=[booking.car_id]):
        if other_booking.id == booking.id:
            continue
        other_date_from, other_date_to = booking_time_range(other_booking)

        if (
            (other_date_from <= date_from < other_date_to)
            or (other_date_from < date_to <= other_date_to)
            or (date_from <= other_date_from and date_to >= other_date_to)
        ):
            return False, "There's already a booking for this time span"

    return True, None


def booking_form(booking: Booking, title, post_target, sess=None):
    car = get_car(sess["auth"])
    return Page(
        title,
        Form(
            Group(
                Div(
                    Label("From", _for="date_from"),
                    Input(type="date", name="date_from", value=booking.date_from),
                ),
                Div(
                    Label("To", _for="date_to"),
                    Input(type="date", name="date_to", value=booking.date_to),
                ),
                style="flex-direction: row",
            ),
            Select(
                *[
                    Option(u, value=u, selected=booking.user == u)
                    for u in connected_users(sess["auth"])
                ],
                name="user",
            ),
            Input(
                type="text",
                name="id",
                value=booking.id,
                style="display:none",
            ),
            Input(
                type="number",
                name="car_id",
                value=booking.car_id,
                style="display:none",
            ),
            Input(
                type="text",
                name="expense_id",
                value=booking.expense_id,
                style="display:none",
            ),
            Input(type="text", name="note", placeholder="note", value=booking.note),
            Div(
                Label("Distance driven ", _for="distance"),
                Div(
                    Input(
                        type="number",
                        name="distance",
                        value=booking.distance,
                        hx_post="/bookings/cost",
                        hx_trigger="input changed",
                        hx_swap="inner_html",
                        hx_target="#cost",
                    ),
                    Input(value=car.distance_unit, readonly=True),
                    style="display: flex",
                ),
            ),
            Div(id="indicator"),
            Small(get_cost_description(booking.distance, sess), id="cost"),
            Button("Save"),
            hx_post=post_target,
            hx_target="#indicator",
            style="flex-direction: column",
        ),
    )


def get_ride_cost(distance: int, sess=None):
    if sess is None:
        return 0
    cost_per_volume = float(costs.get_gas_price())
    c = get_car(sess["auth"])
    return distance * (cost_per_volume * c.fuel_efficiency + c.cost_per_distance)


@app.post("/bookings/cost")
def get_cost_description(distance: int | None, sess=None):
    if distance is None or sess is None:
        return Br(), Br(), Br()
    c = get_car(sess["auth"])
    total = get_ride_cost(distance, sess)
    cost_per_volume = float(costs.get_gas_price())
    return (
        "This ride costs distance x (gas price x fuel efficiency + fixed cost)",
        Br(),
        f"= {distance} {c.distance_unit} x ({round(cost_per_volume, 2)} {c.currency}/{c.volume_unit} x {c.fuel_efficiency} {c.volume_unit} / {c.distance_unit} + {c.cost_per_distance} {c.currency}/{c.distance_unit})",
        Br(),
        f"= {round(total, 1)} {c.currency}",
        Br(),
    )


@app.get("/bookings")
def bookings_page(sess):
    def calendar_url():
        return f"{BASE_URL}/calendar/{calendar_secret(sess)}.ics"

    return Page(
        "Bookings",
        Div(
            A("New Booking", role="button", href="/bookings/add"),
            Button(
                "Copy calendar link",
                _=f"on click call navigator.clipboard.writeText('{calendar_url()}') then set my.innerText to 'Copied!'",
                cls="secondary outline",
            ),
        ),
        Br(),
        Main(
            *[
                Article(
                    Strong(b.note),
                    Div(Icon(svgs.user.regular), b.user),
                    Div(Icon(svgs.clock.regular), bookings_time(b)),
                    Div(
                        A(
                            Icon(svgs.pen.solid),
                            cls="secondary",
                            role="button",
                            href=f"/bookings/edit/{b.id}",
                        ),
                        A(
                            Icon(svgs.trash_can.regular),
                            role="button",
                            hx_delete=f"/bookings/{b.id}",
                            hx_confirm="Are you sure you want to delete this booking?",
                            hx_swap="delete",
                            hx_target="closest article",
                            cls="secondary",
                        ),
                        style="width: auto; margin-bottom: 0",
                        role="group",
                    ),
                    cls="grid",
                    style="align-items: center;",
                )
                for b in get_bookings(sess)
            ],
        ),
    )


def booking_time_range(booking: Booking) -> (datetime, datetime):
    return datetime.fromisoformat(booking.date_from), datetime.fromisoformat(
        booking.date_to
    )


def bookings_time(booking: Booking) -> str:
    date_from, date_to = booking_time_range(booking)
    if date_from.date() == date_to.date():
        return Small(date_from.date())
    else:
        return Small(f"{date_from.date()} - {date_to.date()}")
