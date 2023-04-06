from flask import Flask
from flask import render_template
import sqlite3
from datetime import datetime, date, time
from dateutil import relativedelta

app = Flask(__name__)

# Get a database connection.
def connect_db():
    return sqlite3.connect("db.sqlite3")

# Get start and end dates.
def get_start_end(year, month):
    start = datetime.combine(date(year, month, 1), time(0, 0))
    dt = relativedelta.relativedelta(months=1) # Add a month
    end = start + dt
    return (start, end)

# Get the transactions for the given month.
def get_transactions(year, month):
    transactions = []

    # Connect to DB
    connection = connect_db()
    cursor = connection.cursor()

    # Calculate dates
    (start, end) = get_start_end(year, month)

    # Query transactions
    result = cursor.execute("""
        SELECT timestamp, num, description, amount, category.name
        FROM `transaction`
            JOIN category ON `transaction`.category_id = category.rowid
        WHERE `transaction`.timestamp BETWEEN ? AND ?
        ORDER BY timestamp DESC
    """, (start.timestamp(), end.timestamp()))

    for row in result.fetchall():
        tx_date = datetime.fromtimestamp(row[0])
        transactions.append((tx_date.strftime("%Y-%m-%d"), row[1], row[2], row[3] / 100, row[4]))

    return transactions

# Load categories from the database and total them for the given month (as an int)
def get_categories(year, month):
    categories = []

    # Connect to DB
    connection = connect_db()
    cursor = connection.cursor()

    # Calculate dates
    (start, end) = get_start_end(year, month)

    # Query and sum up categories
    result = cursor.execute("""
        SELECT category.name, SUM(`transaction`.amount)
        FROM `transaction`
            JOIN category ON `transaction`.category_id = category.rowid
        WHERE `transaction`.timestamp BETWEEN ? AND ?
        GROUP BY category.name
    """, (start.timestamp(), end.timestamp()))

    for row in result.fetchall():
        categories.append((row[0], abs(row[1] / 100)))

    return categories

@app.route("/")
def index():
    now = datetime.now()

    categories = get_categories(now.year, now.month)
    transactions = get_transactions(now.year, now.month)
    return render_template('index.html', month=now.month, categories=categories, transactions=transactions)

# if __name__ == '__main__':
#     app.run(host='127.0.0.1', port=5009, debug=True)