from dataclasses import dataclass

from app import app
from config import ADMIN_PASSWORD, ADMIN_USERNAME
from fasthtml.common import *


@dataclass
class Credentials:
    name: str
    password: str


@app.get("/login")
def login_page():
    return Titled(
        "Login",
        Form(
            Input(id="name", placeholder="Name", name="name"),
            Input(
                id="password", type="password", placeholder="Password", name="password"
            ),
            Button("login"),
            action="/login",
            method="post",
        ),
    )


@app.post("/login")
def login(credentials: Credentials, sess):
    if not credentials.name or not credentials.password:
        return RedirectResponse("/login", status_code=303)

    # TODO: Make authentication secure
    if not (
        credentials.name == ADMIN_USERNAME and credentials.password == ADMIN_PASSWORD
    ):
        return RedirectResponse("/login", status_code=303)
    sess["auth"] = credentials.name
    return RedirectResponse("/", status_code=303)


@app.get("/logout")
def get(sess):
    sess["auth"] = None
    return RedirectResponse("/", status_code=303)
