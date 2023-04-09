import sqlite3
from datetime import datetime
from budgetloader import util

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
    (start, end) = util.get_start_end(year, month)

    # Query transactions
    result = cursor.execute("""
        SELECT timestamp, num, description, amount, category.name, `transaction`.rowid, account.name
        FROM `transaction`
            JOIN category ON `transaction`.category_id = category.rowid
            JOIN account ON `transaction`.account_id = account.rowid
        WHERE `transaction`.timestamp BETWEEN ? AND ?
        ORDER BY timestamp DESC
    """, (start.timestamp(), end.timestamp()))

    for row in result.fetchall():
        tx_date = datetime.fromtimestamp(row[0])
        transactions.append({
            "id": row[5], 
            "date": tx_date.strftime("%Y-%m-%d"), 
            "num": row[1], 
            "description": row[2], 
            "amount": row[3] / 100, 
            "category": row[4],
            "account": row[6],
        })

    return transactions

# Load categories from the database and total them for the given month (as an int)
def get_categories(year, month):
    categories = []

    # Connect to DB
    connection = connect_db()
    cursor = connection.cursor()

    # Calculate dates
    (start, end) = util.get_start_end(year, month)

    # Query and sum up categories
    result = cursor.execute("""
        SELECT category.name, category.budget, SUM(COALESCE(`transaction`.amount, 0)), COALESCE(category.budget, 0) + SUM(COALESCE(`transaction`.amount, 0)), category.rowid
        FROM category
            LEFT JOIN `transaction` ON category.rowid = `transaction`.category_id AND `transaction`.timestamp BETWEEN ? AND ?
        GROUP BY category.name
    """, (start.timestamp(), end.timestamp()))

    for row in result.fetchall():
        categories.append({
            "id": row[4], 
            "name": row[0], 
            "budget": row[1], 
            "total": row[2], 
            "leftover": row[3]
        })

    return categories

def get_category(id):
    connection = connect_db()
    cursor = connection.cursor()
    
    result = cursor.execute("""
        SELECT rowid, name, budget FROM category WHERE rowid = ?
    """, (id,))

    row = result.fetchone()
    if not row is None:
        return {"id": row[0], "name": row[1], "budget": row[2]}
    else:
        return None

def save_category(category):
    connection = connect_db()
    cursor = connection.cursor()

    # Check category existence.
    # if cursor.execute("SELECT rowid FROM category WHERE rowid = ?", (category["id"],)).fetchone() is None:
    if category["id"] is None:
        # If it doesn't exist, create it.
        cursor.execute("""
            INSERT INTO category (name, budget)
            VALUES (?, ?)
        """, category["name"], util.to_cents(category["budget"]))
    else:
        # If it does exist, update it.
        cursor.execute("""
            UPDATE category
            SET name = ?, budget = ?
            WHERE rowid = ?
        """, (category["name"], util.to_cents(category["budget"]), category["id"]))
    
    connection.commit()

# Checks for duplicate transactions and removes the one with the lower ID.
def deduplicate_transactions():
    connection = connect_db()
    cursor = connection.cursor()

    # Find the duplicates
    duplicates = cursor.execute("""
        SELECT MIN(rowid), timestamp, num, description, amount, account_id
        FROM `transaction`
        GROUP BY timestamp, num, description, amount, account_id
        HAVING count(*) > 1
    """).fetchall()

    # Delete the duplicates
    for duplicate in duplicates:
        cursor.execute("""
            DELETE FROM `transaction`
            WHERE rowid = ?
        """, (duplicate[0],))
    
    connection.commit()