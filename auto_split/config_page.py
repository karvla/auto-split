from uuid import uuid4

from app import app
from common import db_fields
from components import Page
from db.init_db import load_database
from fasthtml.common import *

db = load_database()
cars = db.t.cars
Car = cars.dataclass()
users = db.t.users
User = users.dataclass()


@app.get("/config/edit")
def edit_config_form(sess=None):
    car, *_ = db.query(
        f"""
        select {db_fields(Car, 'cars')}
        from cars
        join users
        on cars.id = users.car_id
        where users.name = ?
        limit 1
                   """,
        [sess["auth"]],
    )
    car = Car(**car)
    return config_form(
        car,
        "Edit Configuration",
        "/config/edit",
    )


@app.get("/config/new")
def new_config_page(sess=None):
    return config_form(
        Car(
            id=None,
            name=None,
            car_secret=str(uuid4()),
            currency="",
            distance_unit="",
            volume_unit="",
            fuel_efficiency=1.0,
            cost_per_distance=1.0,
        ),
        "Create car-group",
        "/config/new",
    )


def has_access(car: Car, sess=None):
    if sess is None:
        True
    return users.get(sess["auth"]).car_id == car.id


@app.post("/config/edit")
def edit_config(car: Car, sess=None):
    if not has_access(car, sess):
        return Response(status_code=401)
    cars.update(car)
    return Response(headers={"HX-Location": "/config/edit"})


@app.post("/config/new")
def new_config(car: Car, sess=None):
    car.id = None
    car = cars.insert(car)
    user = db.t.users.get(sess["auth"])
    user.car_id = car.id
    db.t.users.update(user)
    return Response(headers={"HX-Location": "/config/edit"})


def config_form(car: Car, title, post_target):
    return Page(
        title,
        Form(
            Input(
                type="text",
                name="id",
                value=car.id,
                style="display:none",
            ),
            Div(
                Label("Car Secret", _for="car_secret"),
                Input(
                    type="text", name="car_secret", value=car.car_secret, readonly=True
                ),
            ),
            Div(
                Label("Name", _for="name"),
                Input(type="text", name="name", value=car.name),
            ),
            Div(
                Label("Currency", _for="currency"),
                Input(type="text", name="currency", value=car.currency),
            ),
            Div(
                Label("Distance Unit", _for="distance_unit"),
                Input(type="text", name="distance_unit", value=car.distance_unit),
            ),
            Div(
                Label("Volume Unit", _for="volume_unit"),
                Input(type="text", name="volume_unit", value=car.volume_unit),
            ),
            Div(
                Label("Fuel Efficiency", _for="fuel_efficiency"),
                Input(type="number", step="0.01", name="fuel_efficiency", value=car.fuel_efficiency),
            ),
            Div(
                Label("Cost per Distance", _for="cost_per_distance"),
                Input(
                    type="number",
                    step="0.01",
                    name="cost_per_distance",
                    value=car.cost_per_distance,
                ),
            ),
            Button("Save"),
            hx_post=post_target,
            style="flex-direction: column",
        ),
    )
