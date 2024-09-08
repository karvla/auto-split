from app import (
    app,
    Page,
    calendar_path,
)
import os
from expenses import Expense, expenses
from db.expense_type import ExpenseType
import costs
from datetime import datetime
from fasthtml.common import (
    Response,
    Small,
    Div,
    Br,
    Main,
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
from db.init_db import db
from itertools import permutations

expenses = db.t.expenses
Expense = expenses.dataclass()
users = db.t.users
User = users.dataclass()


@app.get("/debts")
def debts_page():
    a = [
        Div(f"{d.name} owes {c.name} {total_debt(d, c)}")
        for d, c in permutations(users(), 2)
    ]
    return Page("debts", *a)


def total_debt(debtor: User, creditor):
    return max(0, debt(debtor, creditor) - debt(creditor, debtor))


def debt(debtor: User, creditor: User):
    current_date = datetime.now().date().isoformat()
    from_shared_expenses = next(
        db.query(
            f"""
        select sum(cost) / (select count(name) from {users})
        from {expenses}
        where user == ?
        and type == '{ExpenseType.shared}'
        and date <= ?
        """,
            [creditor.name, current_date],
        )
    )

    from_individual_expenses = next(
        db.query(
            f"""
        select sum(cost)
        from {expenses}
        where user == ?
        and type == '{ExpenseType.individual}'
        and date <= ?
        """,
            [debtor.name, current_date],
        )
    )
    from_shared_expenses = next(iter(from_shared_expenses.values()))
    from_individual_expenses = next(iter(from_individual_expenses.values()))
    if from_shared_expenses is None:
        from_shared_expenses = 0
    if from_individual_expenses is None:
        from_individual_expenses = 0
    return from_shared_expenses + from_individual_expenses
