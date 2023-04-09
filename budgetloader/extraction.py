import sqlite3
import re
import os
from budgetloader import loaders

# Run through the regex table until a category is found. There should be a .* pattern for a default if none found.
def lookup_category(description):
    for (pattern, category_id) in load_patterns():
        regex = re.compile(pattern)
        match = regex.match(description)
        if not match is None:
            return category_id
    return 0

def lookup_account(filename):
    accounts = load_accounts()
    for account in accounts:
        regex = re.compile(account["regex"])
        match = regex.match(filename)
        if not match is None:
            return account
    return None

def lookup_format(filename):
    formats = load_formats()
    for format in formats:
        regex = re.compile(format["regex"])
        match = regex.match(filename)
        if not match is None:
            return format
    return None

# Re-categorizes all transactions as needed.
def update_categories():
    # SQLite connection
    connection = sqlite3.connect("db.sqlite3")
    cursor = connection.cursor()

    result = cursor.execute("SELECT rowid, description FROM `transaction` WHERE category_override = 0")
    all_transactions = result.fetchall()
    connection.commit()

    for row in all_transactions:
        print(row)
        new_category_id = lookup_category(row[1])
        cursor.execute("UPDATE `transaction` SET category_id=? WHERE rowid=?", (new_category_id, row[0]))
    
    connection.commit()

# Inserts a transaction into the database.
def insert_transaction(timestamp, num, description, amount, category_id, account_id):
    # SQLite connection
    connection = sqlite3.connect("db.sqlite3")
    cursor = connection.cursor()
    params = (timestamp, num, description, amount, category_id, account_id)
    existing = cursor.execute("SELECT timestamp, num, description, amount, account_id FROM `transaction`").fetchall()
    if len(existing) == 0:
        cursor.execute("INSERT INTO `transaction` (timestamp, num, description, amount, category_id, account_id) VALUES (?, ?, ?, ?, ?, ?)", params)
        connection.commit()
        return ""
    else:
        return "Duplicate detected."

def load_categories():
    # SQLite connection
    connection = sqlite3.connect("db.sqlite3")
    cursor = connection.cursor()

    categories = {}
    for row in cursor.execute("SELECT rowid, name FROM category"):
        categories[row[0]] = row[1]
    return categories

def load_patterns():
    # SQLite connection
    connection = sqlite3.connect("db.sqlite3")
    cursor = connection.cursor()

    patterns = []
    for row in cursor.execute("SELECT regex, category_id FROM pattern ORDER BY precedence DESC"):
        patterns.append((row[0], row[1]))
    return patterns

def load_formats():
    # SQLite connection
    connection = sqlite3.connect("db.sqlite3")
    cursor = connection.cursor()
    
    formats = []
    for row in cursor.execute("SELECT rowid, name, regex FROM format"):
        formats.append({
            "id": row[0],
            "name": row[1],
            "regex": row[2],
        })
    return formats

def load_accounts():
    # SQLite connection
    connection = sqlite3.connect("db.sqlite3")
    cursor = connection.cursor()

    accounts = []
    for row in cursor.execute("SELECT rowid, name, regex FROM account"):
        accounts.append({
            "id": row[0],
            "name": row[1],
            "regex": row[2],
        })
    return accounts

def load_file(path):
    # Decide which account this file belongs to.
    filename = os.path.basename(path)
    account = lookup_account(filename)
    format = lookup_format(filename)

    # Can't do anything if the format or account is not detected.
    if account is None:
        return "No account matches."

    if format is None:
        return "No format matches."
    
    # Dispatch the file to the proper custom loading function.
    loader = getattr(loaders, format["name"].lower())
    loader(account["id"], path)

    return ""

# TODO:
# - regex detection for account and format on filenames
# - cron job to load automatically
# - budget setting features