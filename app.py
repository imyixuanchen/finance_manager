from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import get_income, get_expenses, login_required, usd, get_date, get_percentage, percentage


app = Flask(__name__)
app.secret_key = "A9F8C7B6E1D2G3H4I5J6K7L8M9N0O1P2"
db = SQL("sqlite:///finance.db")

app.jinja_env.filters["usd"] = usd
app.jinja_env.filters["percentage"] = percentage

INCOME_CATEGORIES = ["Salary", "Extra money", "Plus", "Other"]
EXPENSES_CATEGORIES = ["Food", "Entertainment", "Transport", "Home", "Clothing", "Health", "Education", "Gifts", "Other"]

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    global EXPENSES_CATEGORIES
    user_id = session.get("user_id")
    balance = db.execute("SELECT balance FROM users WHERE id = ?", user_id)[0]["balance"]
    date = get_date()
    income = get_income(user_id, date)
    expenses = get_expenses(user_id, date)

    rows = db.execute("SELECT amount, category, date, id, notes FROM  transactions WHERE user_id = ? AND date LIKE ?", user_id, f"{date}%")

    percentages = {}
    for category in EXPENSES_CATEGORIES:
        percentage = get_percentage(user_id, date, category)
        if percentage > 0:
            percentages[category] = percentage

    return render_template("index.html", balance=balance, date=date, rows=rows, income=income, expenses=expenses, percentages=percentages)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            flash("username is required")
            return redirect(url_for("register"))
        if not password:
            flash("password is required")
            return redirect(url_for("register"))
        if not confirmation:
            flash("confirmation password is required")
            return redirect(url_for("register"))
        if password != confirmation:
            flash("passwords don't match")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)
        try:
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hashed_password)
        except ValueError:
            flash("username is already taken")
            return redirect("register")

        flash("succesfully registered")
        return redirect(url_for("index"))

    else:
        return render_template("register.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            flash("username is required")
            return redirect(url_for("login"))
        if not password:
            flash("password is required")
            return redirect(url_for("login"))

        try:
            user_id = db.execute("SELECT id FROM users WHERE username = ?", username)[0]["id"]
        except IndexError:
            flash("username or password incorrect")
            return redirect(url_for("login"))

        correct_password = db.execute("SELECT hash FROM users WHERE id = ?", user_id)[0]["hash"]
        if not check_password_hash(correct_password, password):
            flash("username or password incorrect")
            return redirect(url_for("login"))

        session["user_id"] = user_id
        return redirect(url_for("index"))

    else:
        return render_template("login.html")



@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/income", methods=["GET", "POST"])
@login_required
def income():
    """Add money into balance"""
    global INCOME_CATEGORIES
    if request.method == "POST":
        user_id = session.get("user_id")
        balance = float(db.execute("SELECT balance FROM users WHERE id = ?", user_id)[0]["balance"])
        category = request.form.get("category")
        date = request.form.get("date")
        notes = request.form.get("notes")

        try:
            amount = float(request.form.get("amount"))
            if not amount:
                flash("amount is required")
                return redirect(url_for("income"))
        except ValueError:
            flash("amount must be numeric")
            return redirect(url_for("income"))
        except TypeError:
            flash("amount is required")
            return redirect(url_for("income"))

        if amount < 0:
            flash("amount must be positive")
            return redirect(url_for("income"))
        if not category:
            flash("category is required")
            return redirect(url_for("income"))
        if category not in INCOME_CATEGORIES:
            flash("select a valid category")
            return redirect(url_for("income"))
        if not date:
            flash("date is required")
            return redirect(url_for("income"))


        db.execute("INSERT INTO transactions (user_id, amount, category, date, notes) VALUES(?, ?, ?, ?, ?)", user_id, amount, category, date, notes)
        balance += amount
        db.execute("UPDATE users SET balance = ? WHERE id = ?", balance, user_id)
        return redirect(url_for("index"))

    else:
        return render_template("income.html", categories=INCOME_CATEGORIES)


@app.route("/expenses", methods=["POST", "GET"])
@login_required
def expenses():
    """Spend money of the balance"""
    global EXPENSES_CATEGORIES
    if request.method == "POST":
        user_id = session.get("user_id")
        balance = float(db.execute("SELECT balance FROM users WHERE id = ?", user_id)[0]["balance"])
        category = request.form.get("category")
        date = request.form.get("date")
        notes = request.form.get("notes")

        try:
            amount = float(request.form.get("amount"))
            if not amount:
                flash("amount is required")
                return redirect(url_for("expenses"))
        except ValueError:
            flash("amount must be numeric")
            return redirect(url_for("expenses"))
        except TypeError:
            flash("amount is required")
            return redirect(url_for("expenses"))

        if amount < 0:
            flash("amount must be positive")
            return redirect(url_for("expenses"))
        if not category:
            flash("category is required")
            return redirect(url_for("expenses"))
        if category not in EXPENSES_CATEGORIES:
            flash("select a valid category")
            return redirect(url_for("expenses"))
        if not date:
            flash("date is required")
            return redirect(url_for("expenses"))

        amount = -amount
        db.execute("INSERT INTO transactions (user_id, amount, category, date, notes) VALUES(?, ?, ?, ?, ?)", user_id, amount, category, date, notes)
        balance += amount
        db.execute("UPDATE users SET balance = ? WHERE id = ?", balance, user_id)
        return redirect(url_for("index"))

    else:
        return render_template("expenses.html", categories=EXPENSES_CATEGORIES)

@app.route("/delete", methods=["POST"])
def delete_row():
    user_id = session.get("user_id")
    balance = float(db.execute("SELECT balance FROM users WHERE id = ?", user_id)[0]["balance"])
    transaction_id = request.form.get("id")
    amount = float(request.form.get("amount"))

    db.execute("DELETE FROM transactions WHERE id = ?", transaction_id)
    balance -= amount
    db.execute("UPDATE users SET balance = ? WHERE id = ?", balance, user_id)

    return redirect(url_for("index"))
