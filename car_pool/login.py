from dataclasses import dataclass

from app import app
from auth import verify_password
from db.init_db import load_database
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
    users = load_database().t.users
    user = users.get(credentials.name)
    if user is None:
        return RedirectResponse("/login", status_code=303)

    if not verify_password(user.password_salt, credentials.password):
        return RedirectResponse("/login", status_code=303)

    sess["auth"] = credentials.name
    return RedirectResponse("/", status_code=303)


@app.get("/logout")
def get(sess):
    sess["auth"] = None
    return RedirectResponse("/", status_code=303)
