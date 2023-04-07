import sqlite3
import sys
import csv
from datetime import datetime
import re
from werkzeug.security import generate_password_hash

# SQLite connection
connection = sqlite3.connect("db.sqlite3")
cursor = connection.cursor()

def reset_password(password):
    hash = generate_password_hash(password)
    with open("hash.txt", "w") as f:
        f.write(hash)

# Run through the regex table until a category is found. There should be a .* pattern for a default if none found.
def lookup_category(description):
    for (pattern, category_id) in patterns:
        regex = re.compile(pattern)
        match = regex.match(description)
        if not match is None:
            return category_id
    return 0

# Re-categorizes all transactions as needed.
def update_categories():
    result = cursor.execute("SELECT rowid, description FROM `transaction` WHERE category_override = 0")
    all_transactions = result.fetchall()
    connection.commit()

    for row in all_transactions:
        print(row)
        new_category_id = lookup_category(row[1])
        cursor.execute("UPDATE `transaction` SET category_id=? WHERE rowid=?", (new_category_id, row[0]))
    
    connection.commit()

# Inserts a transaction into the database.
def insert_transaction(timestamp, num, description, amount, category_id):
    params = (timestamp, num, description, amount, category_id, accounts[account_name])
    cursor.execute("INSERT INTO `transaction` (timestamp, num, description, amount, category_id, account_id) VALUES (?, ?, ?, ?, ?, ?)", params)
    connection.commit()

# Define functions for custom loading. For now this is hard-coded but it could be configurable later. The formats vary wildly though.
def load_omni():
    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            timestamp = int(datetime.strptime(row["Processed Date"], "%Y-%m-%d").timestamp())
            num = row["Check Number"]
            description = row["Description"]
            amount = int(float(row["Amount"]) * 100)
            # Negate amount if debit
            if row["Credit or Debit"] == "Debit":
                amount = -amount
            category_id = lookup_category(description)
            insert_transaction(timestamp, num, description, amount, category_id)

def load_discover():
    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            timestamp = int(datetime.strptime(row["Post Date"], "%m/%d/%Y").timestamp())
            description = row["Description"]
            amount = int(float(row["Amount"]) * -100) # Amount is reversed since this is a credit card
            category_id = lookup_category(description)
            insert_transaction(timestamp, "", description, amount, category_id)

# Load accounts, categories, and regexes for later use.
accounts = {} # name -> rowid
categories = {} # rowid -> name
patterns = [] # list of (regex, category ID) in precedence order (largest first)

for row in cursor.execute("SELECT rowid, name FROM account"):
    accounts[row[1].lower()] = row[0]

for row in cursor.execute("SELECT rowid, name FROM category"):
    categories[row[0]] = row[1]

for row in cursor.execute("SELECT regex, category_id FROM pattern ORDER BY precedence DESC"):
    patterns.append((row[0], row[1]))

# Arguments
# budgetloader [path] --format=[format] --account=[account name]
path = ""
format = "default"
account_name = ""
for arg in sys.argv:
    if arg.startswith("--format"):
        format = arg[9:].lower()
    elif arg.startswith("--path"):
        path = arg[7:]
    elif arg.startswith("--account"):
        account_name = arg[10:].lower()
    elif arg == "--update-categories":
        update_categories()
        print("Categories recalculated.")
    elif arg.startswith("--password"):
        reset_password(arg[11:])
        print("Password reset.")

# Load the data from the file, normalize it, and save it.
if len(path) > 0:
    if format == "omni":
        load_omni()
    elif format == "discover":
        load_discover()

# TODO:
# - regex detection for account and format on filenames
# - cron job to load automatically
# - budget setting features