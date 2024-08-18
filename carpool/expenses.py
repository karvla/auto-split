from app import rt, app, expenses, Expense, users, Page
from datetime import datetime
import os
from fasthtml.common import (
    Response,
    Div,
    Form,
    Titled,
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


@rt("/expenses")
def get():
    return Page(
        "Expenses",
        A("Add expense", href="/expenses/add"),
        Table(
            Tr(Th("Note"), Th("Date"), Th("User"), Th("Amount"), Th(), Th()),
            *[
                Tr(
                    Td(e.note),
                    Td(e.date),
                    Td(e.user),
                    Td(f"{e.cost} {e.currency}"),
                    Td(A("Edit", href=f"/expenses/edit/{e.id}")),
                    Td(
                        Button(
                            "Delete",
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
def get(error_msg=""):
    return expense_form(Expense(), "/expenses/add", "Add expense")


@rt("/expenses/edit/{id}")
def get(id: int):
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
    print(expense)
    currencies = os.getenv("CURRENCIES").split(",")
    if expense.date is None:
        expense.date = datetime.now()
    if expense.cost is None:
        expense.cost = 0
    if expense.currency is None:
        expense.currency = currencies[0]

    return (
        Titled(
            title,
            Form(
                Input(type="text", name="note", placeholder="note", value=expense.note),
                Div(
                    Label("Date", _for="date"),
                    Input(type="date", name="date", value=expense.date),
                ),
                Div(
                    Label("Amount", _for="cost"),
                    Div(
                        Input(type="number", name="cost", value=expense.cost),
                        Select(*[Option(c) for c in currencies], name="currency"),
                        style="display: flex",
                    ),
                ),
                Div(
                    Label("Done by", _for="by"),
                    Select(
                        *[Option(u.name) for u in users()],
                        name="user",
                        value=expense.currency,
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
