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
        SELECT timestamp, num, description, amount, category.name, `transaction`.rowid
        FROM `transaction`
            JOIN category ON `transaction`.category_id = category.rowid
        WHERE `transaction`.timestamp BETWEEN ? AND ?
        ORDER BY timestamp DESC
    """, (start.timestamp(), end.timestamp()))

    for row in result.fetchall():
        tx_date = datetime.fromtimestamp(row[0])
        transactions.append({"id": row[5], "date": tx_date.strftime("%Y-%m-%d"), "num": row[1], "description": row[2], "amount": row[3] / 100, "category": row[4]})

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
        SELECT category.name, category.budget, SUM(`transaction`.amount), COALESCE(category.budget, 0) + SUM(`transaction`.amount), category.rowid
        FROM category
            LEFT JOIN `transaction` ON category.rowid = `transaction`.category_id AND `transaction`.timestamp BETWEEN ? AND ?
        GROUP BY category.name
    """, (start.timestamp(), end.timestamp()))

    for row in result.fetchall():
        categories.append({"id": row[4], "name": row[0], "budget": abs(to_dollars(row[1])), "total": abs(to_dollars(row[2])), "leftover": to_dollars(row[3])})

    return categories

def get_category(id):
    connection = connect_db()
    cursor = connection.cursor()
    
    result = cursor.execute("""
        SELECT rowid, name, budget FROM category WHERE rowid = ?
    """, (id,))

    rows = result.fetchall()
    if len(rows) == 1:
        row = rows[0]
        return {"id": row[0], "name": row[1], "budget": row[2]}
    else:
        return None
