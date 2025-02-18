from datetime import datetime

from auto_split.debts import (
    debt,
    total_debt,
    Expense,
    Transaction,
)
from auto_split.expenses import add_new_expense
from auto_split.db.expense_type import ExpenseType
from test_db import db


def add_expense(user: str, amount: float, type: str):
    expense = Expense(
        id=None,
        title=f"{type.capitalize()} expense",
        note="Test expense",
        date=datetime.now().date(),
        user=user,
        type=type,
        cost=amount,
        currency="USD",
        car_id=1,
    )
    add_new_expense(expense, {"auth": user})


def test_add_shared_expense(db):
    user1, _, _ = db.t.users()
    expenses = db.t.expenses

    add_expense(user1.name, 100, "shared")
    assert len(expenses()) == 1


def test_one_pays_for_gas_that_is_consumed_by_everyone_equally(db):
    user1, user2, user3 = db.t.users()

    add_expense(user1.name, 300, "shared")
    add_expense(user1.name, 100, "individual")
    add_expense(user2.name, 100, "individual")
    add_expense(user3.name, 100, "individual")

    assert total_debt(user1.name, user2.name) == 0
    assert total_debt(user3.name, user2.name) == 0
    assert total_debt(user2.name, user3.name) == 0

    assert total_debt(user3.name, user1.name) == 100
    assert total_debt(user2.name, user1.name) == 100


def test_one_pays_for_gas_and_consumes_it_all(db):
    user1, user2, user3 = db.t.users()

    full_tank = 300
    add_expense(user1.name, full_tank, "shared")
    add_expense(user1.name, full_tank, "individual")

    assert total_debt(user1.name, user2.name) == 0
    assert total_debt(user3.name, user2.name) == 0
    assert total_debt(user2.name, user1.name) == 0
    assert total_debt(user2.name, user3.name) == 0


def test_multiple_people_pay_for_shared_expenses(db):
    user1, user2, user3 = db.t.users()

    add_expense(user1.name, 300, "shared")
    add_expense(user2.name, 150, "shared")

    assert total_debt(user1.name, user2.name) == 0
    assert total_debt(user2.name, user1.name) == 50
    assert total_debt(user3.name, user1.name) == 100
    assert total_debt(user3.name, user2.name) == 50


def test_shared_and_individual_expenses_with_transactions(db):
    user1, user2, user3 = db.t.users()
    transactions = db.t.transactions

    add_expense(user1.name, 300, "shared")
    add_expense(user2.name, 90, "individual")

    transactions.insert(
        Transaction(
            from_user=user3.name,
            to_user=user1.name,
            amount=50,
            date=datetime.now().date().isoformat(),
            currency="USD",
        )
    )

    assert total_debt(user2.name, user1.name) == 300 / 3 + 90 / 3
    assert total_debt(user3.name, user1.name) == 300 / 3 - 50
    assert total_debt(user1.name, user2.name) == 0
    assert total_debt(user3.name, user2.name) == 0
