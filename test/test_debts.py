from datetime import datetime

from test_db import db

from car_pool.debts import (
    Transaction,
    User,
    add_transaction,
    debt,
    delete_transaction,
    total_debt,
    validate_form,
)
from car_pool.expenses import Expense, add_new_expense


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
    )
    add_new_expense(new_expense)

    # Add shared expense for user2
    new_expense = Expense(
        id=None,
        title="Shared Expense",
        note="Test note",
        date=datetime.now().date(),
        user=user2.name,
        type="shared",
        cost=200,
        currency="USD",
    )
    add_new_expense(new_expense)

    assert total_debt(user1, user2) == round((200 / 3 + 100 / (len(db.t.users()) - 1)))
    assert total_debt(user3, user2) == round(200 / 3)
    assert total_debt(user2, user1) == 0
    assert total_debt(user2, user3) == 0


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

    add_transaction(new_transaction)
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

    add_transaction(new_transaction)
    transaction = transactions()[0]

    delete_transaction(transaction.id)
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

    is_valid = validate_form(new_transaction, "amount")
    assert is_valid
