from app import (
    rt,
    app,
    bookings,
    Booking,
    users,
    Page,
    Expense,
    expenses,
    calendar_path,
)
import os
import costs
from datetime import datetime
from fasthtml.common import (
    Response,
    Titled,
    Small,
    Footer,
    Div,
    Br,
    Main,
    P,
    Body,
    Header,
    Form,
    Group,
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


@rt("/bookings")
def get():
    return bookings_page()


@rt("/bookings/add")
def get():
    return booking_form(
        Booking(
            id=None, date_from=None, date_to=None, user=None, note=None, distance=0
        ),
        "Add booking",
        "/bookings/add",
    )


@rt("/bookings/edit/{id}")
def get(id: int):
    return (booking_form(bookings[id], "Edit booking", "/bookings/edit"),)


@app.post("/bookings/add")
def add_new_booking(booking: Booking):
    is_valid, msg = validate_booking(booking)
    booking.id = None
    if not is_valid:
        return msg

    expense_note = "\n".join(
        [p for p in get_cost_description(booking.distance) if type(p) == str]
    )
    expense_id = expenses.insert(
        Expense(
            id=None,
            date=booking.date_from,
            title=f"Ride cost: {booking.note}",
            note=expense_note,
            user=booking.user,
            cost=get_ride_cost(booking.distance),
            currency=os.getenv("CURRENCY"),
        )
    )
    booking.expense_id = expense_id
    bookings.insert(booking)
    return Response(headers={"HX-Location": "/bookings"})


@app.post("/bookings/edit")
def edit_booking(booking: Booking, id: int):
    is_valid, msg = validate_booking(booking)
    if not is_valid:
        return booking_form(booking, "Edit booking", "/bookings/edit")
    bookings.update(booking)
    return Response(headers={"HX-Location": "/bookings"})


@app.post("/bookings/validate")
def edit_booking(booking: Booking):
    is_valid, msg = validate_booking(booking)
    if not is_valid:
        return msg


@app.delete("/bookings/{id}")
def delete_booking(id: int):
    bookings.delete(id)
    return Response(headers={"HX-Location": "/bookings"})


@app.post("/bookings/validate")
def validate_booking(booking: Booking) -> (bool, str | None):
    if not booking.date_from or not booking.date_to:
        return False, "Pls add booking duration"
    if booking.date_from > booking.date_to:
        return False, "Start time should be before end time"
    for b in bookings(where=f"id != {booking.id}"):
        if (
            b.date_from < booking.date_from < b.date_to
            or b.date_from < booking.date_to < b.date_to
            or booking.date_from < b.date_to < booking.date_to
            or booking.date_from < b.date_from < booking.date_to
        ):
            return False, "There's already a booking for this time span"
    return True, None


def booking_form(booking: Booking, title, post_target):
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
            Select(*[Option(u.name) for u in users()], name="user"),
            Input(type="text", name="id", value=booking.id, style="display:none"),
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
                    Input(value=os.getenv("DISTANCE_UNIT"), readonly=True),
                    style="display: flex",
                ),
            ),
            Div(id="indicator"),
            Small(get_cost_description(booking.distance), id="cost"),
            Button("Save"),
            hx_post=post_target,
            hx_target="#indicator",
            style="flex-direction: column",
        ),
    )


def get_ride_cost(distance: int):
    cost_per_volume = float(costs.get_gas_price())
    volume_per_distance = float(os.getenv("FUEL_EFFICIENCY"))
    fixed_cost_per_distance = float(os.getenv("COST_PER_DISTANCE"))
    return distance * (cost_per_volume * volume_per_distance + fixed_cost_per_distance)


@app.post("/bookings/cost")
def get_cost_description(distance: int):
    cost_per_volume = float(costs.get_gas_price())
    volume_per_distance = float(os.getenv("FUEL_EFFICIENCY"))
    fixed_cost_per_distance = float(os.getenv("COST_PER_DISTANCE"))
    volume_unit = os.getenv("VOLUME_UNIT")
    distance_unit = os.getenv("DISTANCE_UNIT")
    currency = os.getenv("CURRENCY")

    total = get_ride_cost(distance)
    return (
        "This ride costs distance x (gas price x fuel efficiency + fixed cost)",
        Br(),
        f"= {distance} {distance_unit} x ({round(cost_per_volume,2)} {currency}/{volume_unit} x {volume_per_distance} {volume_unit} / {distance_unit} + {fixed_cost_per_distance} {currency}/{distance_unit})",
        Br(),
        f"= {round(total,1)} {currency}",
        Br(),
    )


def bookings_page():
    return Page(
        "Bookings",
        Div(
            A("New Booking", href="/bookings/add"),
            Br(),
            A("Calendar", href=calendar_path),
        ),
        Main(
            Table(
                Tr(Th("When"), Th("Note"), Th("User"), Th(), Th()),
                *[
                    Tr(
                        Td(f"{b.date_from} {b.date_to}"),
                        Td(b.note),
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
                    for b in bookings(order_by="date_from")
                    if datetime.fromisoformat(b.date_to) > datetime.now()
                ],
                cls="striped",
            ),
            cls="overflow-auto",
        ),
    )
