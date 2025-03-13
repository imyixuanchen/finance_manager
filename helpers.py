import datetime
from functools import wraps

from cs50 import SQL
from flask import redirect, request, session


db = SQL("sqlite:///finance.db")


def get_date():
    date = request.form.get("date")
    if not date:
        date = datetime.date.today()
        date = date.strftime("%Y-%m")
    return date

def get_expenses(user_id, date):
    expenses = db.execute("SELECT SUM(amount) AS amount FROM transactions WHERE user_id = ? AND date LIKE ? AND amount < 0", user_id, f"{date}%")[0]["amount"]
    if not expenses:
        expenses = 0
    return abs(expenses)


def get_income(user_id, date):
    income = db.execute("SELECT SUM(amount) AS amount FROM transactions WHERE user_id = ? AND date LIKE ? AND amount > 0", user_id, f"{date}%")[0]["amount"]
    if not income:
        income = 0
    return income


def get_percentage(user_id, date, category):
    total = get_expenses(user_id, date)
    category_amount = db.execute("SELECT SUM(amount) AS amount FROM transactions WHERE user_id = ? AND date LIKE ? AND category = ?", user_id, f"{date}%", category)[0]["amount"]
    if category_amount is None:
        return 0
    percentage = round(abs(category_amount) / total, 2)
    return percentage


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def usd(value):
    return f"{value:,.2f}$"


def percentage(value):
    value = value * 100
    return f"{int(value)}%"
