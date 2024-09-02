from enum import Flag, auto


class ExpenseType(Flag):
    shared = auto()
    individual = auto()
