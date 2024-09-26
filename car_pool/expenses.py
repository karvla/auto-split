from dataclasses import fields
from datetime import datetime

from app import app
from common import connected_users
from components import Icon, Page
from config import CURRENCY
from db.expense_type import ExpenseType
from db.init_db import load_database
from fa6_icons import svgs
from fasthtml.common import *

db = load_database()
expenses = db.t.expenses
Expense = expenses.dataclass()
users = db.t.users
User = users.dataclass()


def get_expenses(sess):
    return map(
        lambda b: Expense(**b),
        db.query(
            f"""
    select expenses.{',expenses.'.join(map(lambda f: f.name, fields(Expense)))}
    from expenses
    left join users
    on users.car_id = expenses.car_id
    where users.name = ?
                        """,
            [sess["auth"]],
        ),
    )


def has_access(expense: Expense, sess):
    if sess is None:
        return True
    return (
        db.t.users.count_where(
            "name = ? and car_id = ?", [sess["auth"], expense.car_id]
        )
        > 0
    )


@app.get("/expenses")
def get_expenses_page(sess):
    return Page(
        "Expenses",
        Div(
            A("Add expense", href="/expenses/add", role="button"),
        ),
        Br(),
        Main(
            *[
                Article(
                    Strong(e.title),
                    Div(Icon(svgs.clock.regular), e.date),
                    Div(Icon(svgs.user.regular), e.user),
                    Div(Icon(svgs.coins.solid), f"{round(e.cost)} {e.currency}"),
                    Div(
                        Button(
                            Icon(svgs.pen.solid),
                            cls="secondary",
                            hx_get=f"/expenses/edit/{e.id}",
                            hx_target="body",
                        ),
                        Button(
                            Icon(svgs.trash_can.regular),
                            hx_delete=f"/expenses/{e.id}",
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
                for e in get_expenses(sess)
            ],
        ),
    )


@app.get("/expenses/add")
def add_expenses_page(sess, error_msg=""):
    user_name = sess["auth"]
    user_car, *_ = db.t.users.rows_where("name = ?", [user_name])
    return expense_form(
        Expense(
            id=None,
            title=None,
            note=None,
            date=datetime.now().date(),
            user=user_name,
            type=ExpenseType.individual,
            cost=0,
            car_id=user_car["car_id"],
        ),
        "/expenses/add",
        "Add expense",
        connected_users(sess["auth"]),
    )


@app.get("/expenses/edit/{id}")
def edit_expense_form(id: int, sess=None):
    expense = expenses[id]
    if not has_access(expense, sess):
        return RedirectResponse("/expenses", status_code=401)
    return expense_form(expense, "/expenses/edit", "Edit expense")


@app.post("/expenses/add")
def add_new_expense(expense: Expense, sess=None):
    expense.id = None
    if not has_access(expense, sess):
        return RedirectResponse("/expenses", status_code=401)
    is_valid, msg = validate_expense(expense)
    if not is_valid:
        return msg
    expenses.insert(expense)
    return Response(headers={"HX-Location": "/expenses"})


@app.post("/expenses/edit")
def edit_expense(expense: Expense, id: int, sess=None):
    if not has_access(expense, sess):
        return RedirectResponse("/expenses", status_code=401)
    is_valid, msg = validate_expense(expense)
    if not is_valid:
        return expense_form(expense, "/expenses/edit", "Edit expense")
    expenses.update(expense)
    return Response(headers={"HX-Location": "/expenses"})


@app.delete("/expenses/{id}")
def delete_expense(id: int, sess=None):
    if not has_access(expenses[id], sess):
        return Response("/expenses", status_code=401)
    expenses.delete(id)


@app.post("/expenses/validate")
def validate_expense(expense: Expense, sess=None) -> (bool, str | None):
    if not has_access(expense, sess):
        return RedirectResponse("/expenses", status_code=401)
    if expense.cost is None or expense.cost <= 0.0:
        return False, "Please enter an amount"
    return True, None


def expense_form(expense: Expense, post_target, title, user_names):
    print(expense)

    return (
        Page(
            title,
            Form(
                Input(
                    type="text", name="title", placeholder="title", value=expense.title
                ),
                Textarea(expense.note, type="text", name="note", placeholder="note"),
                Div(
                    Label("Date", _for="date"),
                    Input(type="date", name="date", value=expense.date),
                ),
                Div(
                    Label("Amount", _for="cost"),
                    Div(
                        Input(type="number", name="cost", value=expense.cost),
                        Input(
                            name="currency",
                            value=CURRENCY,
                            aria_label="Read-only input",
                        ),
                        style="display: flex",
                    ),
                ),
                Div(
                    Label("Payed by", _for="by"),
                    Select(
                        *[
                            Option(u, value=u, selected=expense.user == u)
                            for u in user_names
                        ],
                        name="user",
                    ),
                ),
                Legend("Expense type:"),
                Fieldset(
                    Label(
                        Input(
                            type="radio",
                            checked=expense.type == ExpenseType.individual,
                            id="type-individual",
                            name="type",
                            value=ExpenseType.individual,
                        ),
                        Span("Individual", Small("- eg. Consuming gas")),
                        _for="type-individual",
                    ),
                    Label(
                        Input(
                            type="radio",
                            checked=expense.type == ExpenseType.shared,
                            id="type-shared",
                            name="type",
                            value=ExpenseType.shared,
                        ),
                        Span("Shared", Small("- eg. Insurance or buying gas")),
                    ),
                ),
                Input(type="text", name="id", value=expense.id, style="display:none"),
                Input(
                    type="number",
                    name="car_id",
                    value=expense.car_id,
                    style="display:none",
                ),
                Div(id="indicator"),
                Button("Save"),
                hx_post=post_target,
                hx_target="#indicator",
                style="flex-direction: column",
            ),
        ),
    )
