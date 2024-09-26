from dataclasses import fields

from app import app
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
                    select cars.{',cars.'.join(map(lambda f: f.name, fields(Car)))}
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
                Input(type="text", name="car_secret", value=car.car_secret),
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
                Input(type="number", name="fuel_efficiency", value=car.fuel_efficiency),
            ),
            Div(
                Label("Cost per Distance", _for="cost_per_distance"),
                Input(
                    type="number",
                    name="cost_per_distance",
                    value=car.cost_per_distance,
                ),
            ),
            Button("Save"),
            hx_post=post_target,
            style="flex-direction: column",
        ),
    )
