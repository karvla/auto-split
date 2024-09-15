from datetime import datetime
from itertools import permutations
from operator import itemgetter

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

transactions = db.t.transactions
Transaction = transactions.dataclass()


@app.get("/debts")
def debts_page():
    (debtor, creditor, debt), *_ = sorted(all_debts(), key=itemgetter(2), reverse=True)
    transaction = Transaction(
        from_user=debtor.name,
        to_user=creditor.name,
        amount=debt,
    )
    return Page("Debts", debts_form(transaction, debt > 0), transaction_list())


def transaction_list():
    return Div(
        H4("Transactions"),
        current_debt(),
        Div(
            *[transaction_card(t) for t in transactions(order_by="date")],
        ),
        id="transactions-list",
    )


def transaction_card(t: Transaction):
    return Article(
        P(f"{t.from_user} payed {t.to_user} {t.amount} {t.currency}"),
        Span(
            t.date,
            Button(
                Icon(svgs.trash_can.regular),
                cls="secondary",
                hx_delete=f"/debts/transactions/{t.id}",
                hx_target="#transactions-list",
                hx_swap="outerHTML",
            ),
        ),
        style="display: flex; justify-content: space-between; align-items: center",
    )


@app.post("/debts/transactions")
def add_transaction(transaction: Transaction):
    transaction.date = datetime.now().date().isoformat()
    transactions.insert(transaction)
    return transaction_list()


@app.delete("/debts/transactions/{id}")
def delete_transaction(id: int):
    transactions.delete(id)
    return transaction_list()


@app.post("/debts/validate/{input}")
def validate_form(transaction: Transaction, input: str):
    if input == "from" and transaction.from_user == transaction.to_user:
        transaction.to_user = next(
            users.rows_where("name != ?", [transaction.from_user])
        )["name"]
    if input == "to" and transaction.from_user == transaction.to_user:
        transaction.from_user = next(
            users.rows_where("name != ?", [transaction.to_user])
        )["name"]

    if input != "amount":
        transaction.amount = total_debt(
            User(name=transaction.from_user), User(name=transaction.to_user)
        )
    valid = transaction.amount > 0
    return debts_form(transaction, valid)


def debts_form(transaction: Transaction, is_valid):
    currency = CURRENCY
    return Form(
        Div(
            Div(
                Select(
                    *[
                        Option(
                            u.name,
                            selected=u.name == transaction.from_user,
                        )
                        for u in users()
                    ],
                    name="from_user",
                    hx_post="/debts/validate/from",
                    hx_target="closest form",
                ),
                P("pays"),
                style="display: flex; align-items: center; gap: 1em",
            ),
            Div(
                Input(
                    type="number",
                    style="width: 100px",
                    value=transaction.amount,
                    name="amount",
                    id="#amount",
                    hx_post="/debts/validate/amount",
                    hx_target="closest form",
                ),
                Input(
                    value=currency,
                    aria_label="Read-only input",
                    name="currency",
                    style="width: 80px",
                ),
                style="display: flex",
            ),
            Div(
                P("to"),
                Select(
                    *[
                        Option(
                            u.name,
                            selected=u.name == transaction.to_user,
                        )
                        for u in users()
                    ],
                    name="to_user",
                    hx_post="/debts/validate/to",
                    hx_target="closest form",
                ),
                style="display: flex; align-items: center; gap: 1em",
            ),
            Button(
                "Settle up!",
                disabled=not is_valid,
                style="margin-bottom: var(--pico-spacing)",
                hx_post="/debts/transactions",
                hx_target="#transactions-list",
                hx_swap="outerHTML",
                _="on click set {value: '0'} on the first <input/> then add @disabled on me",
            ),
            cls="grid",
            style="align-items: center; justify-content: space-between; gap: 1em",
        ),
    )


def all_debts() -> [(User, User, float)]:
    return [(a, b, total_debt(a, b)) for a, b in permutations(users(), 2)]


def current_debt():
    currency = CURRENCY
    return Div(
        *[
            Small(f"{a.name} owes {b.name} {round(d)} {currency}")
            for a, b, d in all_debts()
            if d > 0
        ]
    )


def total_debt(debtor: User, creditor):
    return round(max(0, debt(debtor, creditor) - debt(creditor, debtor)))


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

    from_transactions = next(
        db.query(
            f"""
        select sum(amount)
        from {transactions}
        where from_user == ?
        and to_user == ?
        """,
            [debtor.name, creditor.name],
        )
    )

    from_shared_expenses = next(iter(from_shared_expenses.values()))
    from_individual_expenses = next(iter(from_individual_expenses.values()))
    from_transactions = next(iter(from_transactions.values()))
    if from_shared_expenses is None:
        from_shared_expenses = 0
    if from_individual_expenses is None:
        from_individual_expenses = 0
    if from_transactions is None:
        from_transactions = 0
    return from_shared_expenses + from_individual_expenses - from_transactions
