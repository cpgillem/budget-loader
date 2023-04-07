import sqlite3
from datetime import datetime, date, time
from budgetloader.util import to_dollars, get_start_end

# Get a database connection.
def connect_db():
    return sqlite3.connect("db.sqlite3")

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
        SELECT category.name, category.budget, SUM(`transaction`.amount), COALESCE(category.budget, 0) + SUM(`transaction`.amount)
        FROM category
            LEFT JOIN `transaction` ON category.rowid = `transaction`.category_id AND `transaction`.timestamp BETWEEN ? AND ?
        GROUP BY category.name
    """, (start.timestamp(), end.timestamp()))

    for row in result.fetchall():
        categories.append((row[0], to_dollars(row[1]), abs(to_dollars(row[2])), to_dollars(row[3])))

    return categories