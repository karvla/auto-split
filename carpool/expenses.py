from app import app, Page
from db.init_db import db
from db.expense_type import ExpenseType
from datetime import datetime
import os
from fasthtml.common import (
    Legend,
    Fieldset,
    Response,
    Textarea,
    Div,
    Form,
    A,
    Table,
    Tr,
    Td,
    Th,
    Button,
    Input,
    Small,
    Span,
    Label,
    Select,
    Option,
)

expenses = db.t.expenses
Expense = expenses.dataclass()
users = db.t.users


@app.get("/expenses")
def get_expenses_page():
    return Page(
        "Expenses",
        A("Add expense", href="/expenses/add", role="button"),
        Table(
            Tr(Th("Note"), Th("Date"), Th("User"), Th("Amount"), Th(), Th()),
            *[
                Tr(
                    Td(e.title),
                    Td(e.date),
                    Td(e.user),
                    Td(f"{round(e.cost)} {e.currency}"),
                    Td(A("edit", href=f"/expenses/edit/{e.id}")),
                    Td(
                        A(
                            "delete",
                            hx_delete=f"/expenses/{e.id}",
                            hx_confirm="Are you sure you want to delete this expense?",
                            hx_swap="delete",
                            hx_target="closest tr",
                        )
                    ),
                )
                for e in expenses()
            ],
            cls="striped",
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
    return True, None


def expense_form(expense: Expense, post_target, title):
    currency = os.getenv("CURRENCY")

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
                        Input(name="currency", value=currency, disabled=True),
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
