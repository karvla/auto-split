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
def debts_page(sess):
    user = sess["auth"]
    (debtor, creditor, debt), *_ = sorted(
        all_debts(user), key=itemgetter(2), reverse=True
    )
    transaction = Transaction(
        from_user=debtor,
        to_user=creditor,
        amount=debt,
    )
    users = connected_users(sess["auth"])
    return Page(
        "Debts", debts_form(transaction, users, debt > 0), transaction_list(user)
    )


def transaction_list(user: str):
    return Div(
        H4("Transactions"),
        current_debt(user),
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
def add_transaction(transaction: Transaction, sess=None):
    if not has_access(transaction, sess):
        return Response(status_code=401)

    transaction.date = datetime.now().date().isoformat()
    transactions.insert(transaction)
    return transaction_list(sess["auth"])


@app.delete("/debts/transactions/{id}")
def delete_transaction(id: int, sess=None):
    t = transactions.get(id)
    if not has_access(t, sess):
        return Response(status_code=401)
    transactions.delete(id)
    return transaction_list(sess["auth"])


@app.post("/debts/validate/{input}")
def validate_form(transaction: Transaction, input: str, sess=None):
    if input == "from" and transaction.from_user == transaction.to_user:
        transaction.to_user = next(
            users.rows_where("name != ?", [transaction.from_user])
        )["name"]
    if input == "to" and transaction.from_user == transaction.to_user:
        transaction.from_user = next(
            users.rows_where("name != ?", [transaction.to_user])
        )["name"]

    if input != "amount":
        transaction.amount = float(
            total_debt(transaction.from_user, transaction.to_user)
        )
    valid = transaction.amount > 0
    return debts_form(transaction, connected_users(sess["auth"]), valid)


def debts_form(transaction: Transaction, users: list[str], is_valid: bool):
    currency = CURRENCY
    return Form(
        Div(
            Div(
                Select(
                    *[
                        Option(
                            user,
                            value=user,
                            selected=user == transaction.from_user,
                        )
                        for user in users
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
                    value=transaction.amount if transaction.amount else "0",
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
                            user,
                            value=user,
                            selected=user == transaction.to_user,
                        )
                        for user in users
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


def all_debts(user: str) -> [(str, str, float)]:
    return [(a, b, total_debt(a, b)) for a, b in permutations(connected_users(user), 2)]


def current_debt(user: str):
    currency = CURRENCY
    return Div(
        *[
            (Small(f"{a} owes {b} {round(d)} {currency}"), Br())
            for a, b, d in all_debts(user)
            if d > 0
        ]
    )


def total_debt(debtor: str, creditor: str):
    return round(max(0, debt(debtor, creditor) - debt(creditor, debtor)))


def connected_users(user: str):
    return list(
        map(
            lambda x: next(iter(x.values())),
            db.query(
                """
            select name
            from users
            where car_id = (
                select car_id
                from users
                where name = ?
                limit 1
            )
            """,
                [user],
            ),
        )
    )


def debt(debtor: str, creditor: str):
    current_date = datetime.now().date().isoformat()
    all_users = connected_users(debtor)
    from_shared_expenses = next(
        db.query(
            f"""
        SELECT
            SUM(cost) / {len(all_users)}
        FROM expenses
        WHERE expenses.user = ?
            AND expenses.type = ?
            AND expenses.date <= ?
        """,
            [
                creditor,
                ExpenseType.shared,
                current_date,
            ],
        ),
        None,  # Default value if nothing is found
    )

    from_individual_expenses = next(
        db.query(
            f"""
        SELECT SUM(cost) / {len(all_users) - 1}
        FROM expenses
        WHERE expenses.user = ?
            AND expenses.type = ?
            AND expenses.date <= ?
            """,
            [
                debtor,
                ExpenseType.individual,
                current_date,
            ],
        ),
        None,  # Default value if no results are returned
    )

    from_transactions = next(
        db.query(
            """
        SELECT SUM(amount)
        FROM transactions
        WHERE from_user = ?
            AND to_user = ?
            """,
            [debtor, creditor],
        ),
        None,  # Default value if no results are returned
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


def has_access(transaction: Transaction, sess):
    if sess is None:
        return True
    users = connected_users(sess["auth"])
    return transaction.from_user in users and transaction.to_user in users
