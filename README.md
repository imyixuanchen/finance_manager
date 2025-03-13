# PERSONAL FINANCE MANAGER
#### Video Demo:  <https://youtu.be/Qaziv-iTJnU>
#### Description:
Personal Finance Manager is a minimal web application that allows the user to track its monthly finances, including their income and expenses organised in different categories.

#### Usage
First, the you should create an account and log in.
Once you are logged in it will redirect you to the homepage. On the top of the homepage it appears the date formatted in YYYY-MM, below their is a label that enables the user to change the monthly view.
Currently you won't be able to see your transactions because you haven't done any yet. You will see on the nav bar tow different buttons "Add money" and "Spend money". If you click them it will redirect you to another page with a form. Here you can submit the amount of maney that you want to deposit or spend, select the category of the transaction (where it came from or where did you spent it), the date and some notes.
Once done it will redirect you to the homepage, here you will see all your transactions of the month (amount, category, date, notes) with your current balance, expenses and income of the month. Also there is an option of deleting the transation if you want to.
Below you will see the percentage of your expenses so you can be conscious on what you are spending.

#### Code walkthrough
##### app.py
* `app.py` is the main file of the web application written in Python with the Flask framework.
It includes a `login`, `register` and `logout` function and the main features of the app.
* The `income` function is the back-end of `income.html` that handles the deposited amount, the categories, the date and the notes. It will update the balance and insert the transaction into the database.
* The `expenses` funtion does the same thing as `income` but with `expenses.html`.
* Finally we have `delete_row`, it is the function that enables the user to delete a row (deleting it from the database).

##### helpers.py
* `helpers.py` is a file that has some of the modules for the application such as `login_required` that forces the user to loggin to be able to use the app.
* `get_date` is a function that gets the current date (YYYY-MM) required for setting the default date.
* `get_income` and `get_expenses` are the function responsible for getting the total expenses/income of the month.
* `get_percentage` is the function that gets the percentage of expenses of each category for the month.
* `usd` and `percentage` are Jinja filters to format currency and percentages.

##### /templates
In `/templates` there are the main HTML templates for the main layout, the login and registration page, the homepage, the add money and spend money page.
They are formatted with Bootstrap and CSS.

##### finance.db
`finance.db` is the main database of the application that registers the users into the `users` table (user id, username, hashed password and balance).
It also keeps track of the transactions in the `transactions` (transaction id, user id, amount, category, date, notes).



