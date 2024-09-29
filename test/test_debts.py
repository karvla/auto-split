from datetime import datetime

from debts import (
    Transaction,
    User,
    add_transaction,
    debt,
    delete_transaction,
    total_debt,
    validate_form,
)
from expenses import Expense, add_new_expense
from test_db import db


def test_add_individual_expense(db):
    expenses = db.t.expenses

    new_expense = Expense(
        id=None,
        title="Individual Expense",
        note="Test note",
        date=datetime.now().date(),
        user="user1",
        type="individual",
        cost=100,
        currency="USD",
        car_id=1,
    )

    add_new_expense(new_expense)
    assert len(expenses()) == 1


def test_add_shared_expense(db):
    expenses = db.t.expenses

    new_expense = Expense(
        id=None,
        title="Shared Expense",
        note="Test note",
        date=datetime.now().date(),
        user="user2",
        type="shared",
        cost=200,
        currency="USD",
        car_id=1,
    )

    add_new_expense(new_expense)
    assert len(expenses()) == 1


def test_total_debt(db):
    user1, user2, user3 = db.t.users()

    new_expense = Expense(
        id=None,
        title="Individual Expense",
        note="Test note",
        date=datetime.now().date(),
        user=user1.name,
        type="individual",
        cost=100,
        currency="USD",
        car_id=1,
    )
    add_new_expense(new_expense, {"auth": user1.name})

    new_expense = Expense(
        id=None,
        title="Shared Expense",
        note="Test note",
        date=datetime.now().date(),
        user=user2.name,
        type="shared",
        cost=200,
        currency="USD",
        car_id=1,
    )
    add_new_expense(new_expense, {"auth": user1.name})

    assert total_debt(user1.name, user2.name) == round((200 / 3 + 100 / (3 - 1)))
    assert total_debt(user3.name, user2.name) == round(200 / 3)
    assert total_debt(user2.name, user1.name) == 0
    assert total_debt(user2.name, user3.name) == 0


def test_add_transaction(db):
    transactions = db.t.transactions
    user1, user2, user3 = db.t.users()

    new_transaction = Transaction(
        id=None,
        from_user=user1.name,
        to_user=user2.name,
        amount=50,
        currency="USD",
        date=datetime.now().date().isoformat(),
    )

    add_transaction(new_transaction, {"auth": user1.name})
    assert len(transactions()) == 1


def test_delete_transaction(db):
    transactions = db.t.transactions
    user1, user2, user3 = db.t.users()

    new_transaction = Transaction(
        id=None,
        from_user="user1",
        to_user="user2",
        amount=50,
        currency="USD",
        date=datetime.now().date().isoformat(),
    )

    add_transaction(new_transaction, {"auth": user1.name})
    transaction = transactions()[0]

    delete_transaction(transaction.id, {"auth": user1.name})
    assert len(transactions()) == 0


def test_validate_form(db):
    users = db.t.users
    user1, user2, user3 = db.t.users()

    new_transaction = Transaction(
        id=None,
        from_user=user1.name,
        to_user=user2.name,
        amount=50,
        currency="USD",
        date=datetime.now().date().isoformat(),
    )

    is_valid = validate_form(new_transaction, "amount", {"auth": user1.name})
    assert is_valid
