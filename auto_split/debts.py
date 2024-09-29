from datetime import datetime
from itertools import permutations
from operator import itemgetter

from app import app
from common import connected_users, get_car
from components import Icon, Page
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
    users = connected_users(sess["auth"])
    if len(users) < 2:
        return Page(
            "Debts",
            "No debts since you are the only one in this group",
        )

    (debtor, creditor, debt), *_ = sorted(
        all_debts(user), key=itemgetter(2), reverse=True
    )
    transaction = Transaction(
        from_user=debtor,
        to_user=creditor,
        amount=debt,
    )
    return Page(
        "Debts",
        debts_form(transaction, debt > 0, sess),
        transaction_list(user),
        users_list(user),
    )


def transaction_list(user: str):
    users = connected_users(user)
    question_marks = ",".join(("?" for _ in users))
    return Div(
        H4("Transactions"),
        current_debt(user),
        Div(
            *[
                transaction_card(t)
                for t in transactions(
                    where=f"""
                    to_user in ({question_marks})
                    or from_user in ({question_marks})
                    """,
                    where_args=users + users,
                    order_by="date desc",
                )
            ],
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
    return debts_form(transaction, valid, sess)


def debts_form(transaction: Transaction, is_valid: bool, sess):
    currency = get_car(sess["auth"])
    users = connected_users(sess["auth"])
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
    currency = get_car(user).currency
    return Div(
        *[
            (Small(f"{a} owes {b} {round(d)} {currency}"), Br())
            for a, b, d in all_debts(user)
            if d > 0
        ]
    )


def total_debt(debtor: str, creditor: str):
    return round(max(0, debt(debtor, creditor) - debt(creditor, debtor)))


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


@app.delete("/users/{user_name}")
def delete_user(user_name: str, sess=None):
    print(user_name)
    if not can_delete_user(user_name, sess):
        return Response(status_code=401)
    user = users.get(user_name)
    print(user)
    user.car_id = None
    users.upsert(user)
    if user_name == sess["auth"]:
        return RedirectResponse("/logout", status_code=302)


def can_delete_user(user: str, sess=None):
    if sess is None:
        return True
    return user in connected_users(sess["auth"])


def users_list(user: str):
    all_users = connected_users(user)
    return Details(
        Summary(Strong("Users")),
        *[
            Article(
                u,
                Button(
                    Icon(svgs.trash_can.regular),
                    hx_delete=f"/users/{u}",
                    hx_target="closest article",
                    hx_swap="outerHTML",
                    hx_confirm=f"Are you sure you want to remove {u} from this group?",
                    cls="secondary",
                ),
                style="display: flex; justify-content: space-between; align-items: center",
            )
            for u in all_users
        ],
    )
