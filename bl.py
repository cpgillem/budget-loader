from budgetloader import extraction, data
import sys
from werkzeug.security import generate_password_hash
import sqlite3

def load_accounts():
    # SQLite connection
    connection = sqlite3.connect("db.sqlite3")
    cursor = connection.cursor()

    accounts = {}
    for row in cursor.execute("SELECT rowid, name, regex FROM account"):
        accounts[row[1].lower()] = row[0]
    return accounts

def reset_password(password):
    hash = generate_password_hash(password)
    with open("hash.txt", "w") as f:
        f.write(hash)

# Load accounts, categories, and regexes for later use.
accounts = load_accounts() # name -> rowid
categories = extraction.load_categories() # rowid -> name
patterns = extraction.load_patterns() # list of (regex, category ID) in precedence order (largest first)

# Arguments
# budgetloader [path] --format=[format] --account=[account name]
path = ""
format = "default"
account_name = ""
for arg in sys.argv:
    if arg.startswith("--path"):
        path = arg[7:]
    elif arg == "--update-categories":
        extraction.update_categories()
        print("Categories recalculated.")
    elif arg == "--deduplicate":
        data.deduplicate_transactions()
        print("Duplicates removed.")
    elif arg.startswith("--password"):
        reset_password(arg[11:])
        print("Password reset.")

# Load the data from the file, normalize it, and save it.
if len(path) > 0:
    print(extraction.load_file(path))

# TODO: 
# - File upload
# - Organize routes
# - Transaction editing/adding manually
# - Sinking funds/longer term budgets
# - Carry-over budgets