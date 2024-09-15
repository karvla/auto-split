from datetime import datetime

from app import app
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


@app.get("/expenses")
def get_expenses_page():
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
                for e in expenses()
            ],
        ),
    )


@app.get("/expenses/add")
def add_expenses_page(error_msg=""):
    return expense_form(
        Expense(
            id=None,
            title=None,
            note=None,
            date=datetime.now().date(),
            user=None,
            type=ExpenseType.individual,
            cost=0,
        ),
        "/expenses/add",
        "Add expense",
    )


@app.get("/expenses/edit/{id}")
def edit_expense_form(id: int):
    return expense_form(expenses[id], "/expenses/edit", "Edit expense")


@app.post("/expenses/add")
def add_new_expense(expense: Expense):
    is_valid, msg = validate_expense(expense)
    expense.id = None
    if not is_valid:
        return msg
    expenses.insert(expense)
    return Response(headers={"HX-Location": "/expenses"})


@app.post("/expenses/edit")
def edit_expense(expense: Expense, id: int):
    is_valid, msg = validate_expense(expense)
    if not is_valid:
        return expense_form(expense, "/expenses/edit", "Edit expense")
    expenses.update(expense)
    return Response(headers={"HX-Location": "/expenses"})


@app.delete("/expenses/{id}")
def delete_expense(id: int):
    expenses.delete(id)


@app.post("/expenses/validate")
def validate_expense(expense: Expense) -> (bool, str | None):
    if expense.cost is None or expense.cost <= 0.0:
        return False, "Please enter an amount"
    return True, None


def expense_form(expense: Expense, post_target, title):

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
                            Option(u.name, selected=u.name == expense.user)
                            for u in users()
                        ],
                        name="user",
                        value=expense.currency,
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
                Div(id="indicator"),
                Button("Save"),
                hx_post=post_target,
                hx_target="#indicator",
                style="flex-direction: column",
            ),
        ),
    )
