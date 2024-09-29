from datetime import datetime

from expenses import (
    Expense,
    add_new_expense,
    delete_expense,
    edit_expense,
    validate_expense,
)
from test_db import db


def test_users_table(db):
    users = db.t.users
    assert users.exists()


def test_add_new_expense(db):
    expenses = db.t.expenses

    new_expense = Expense(
        id=None,
        title="Test Expense",
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


def test_edit_expense(db):
    expenses = db.t.expenses

    new_expense = Expense(
        id=None,
        title="Test Expense",
        note="Test note",
        date=datetime.now().date(),
        user="user1",
        type="individual",
        cost=100,
        currency="USD",
        car_id=1,
    )

    add_new_expense(new_expense)
    expense = expenses()[0]
    expense.note = "Updated note"

    response = edit_expense(expense, expense.id)
    assert response.headers["HX-Location"] == "/expenses"
    assert expenses[expense.id].note == "Updated note"


def test_validate_expense(db):
    expenses = db.t.expenses

    new_expense = Expense(
        id=None,
        title="Test Expense",
        note="Test note",
        date=datetime.now().date(),
        user="user1",
        type="individual",
        cost=100,
        currency="USD",
        car_id=1,
    )

    is_valid, msg = validate_expense(new_expense)
    assert is_valid


def test_validate_expense(db):
    expenses = db.t.expenses

    new_expense = Expense(
        id=None,
        title="Test Expense",
        note="Test note",
        date=datetime.now().date(),
        user="user1",
        type="individual",
        cost=None,
        currency="USD",
        car_id=1,
    )

    is_valid, msg = validate_expense(new_expense)
    assert not is_valid


def test_delete_expense(db):
    expenses = db.t.expenses

    new_expense = Expense(
        id=None,
        title="Test Expense",
        note="Test note",
        date=datetime.now().date(),
        user="user1",
        type="individual",
        cost=100,
        currency="USD",
        car_id=1,
    )

    add_new_expense(new_expense)
    expense = expenses()[0]

    delete_expense(expense.id)
    assert len(expenses()) == 0
