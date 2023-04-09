import csv
from datetime import datetime
from budgetloader import extraction

# Define functions for custom loading. For now this is hard-coded but it could be configurable later. The formats vary wildly though.
# When a new format is defined in the `format` table, just create a function that matches its name.

def omni(account_id, path):
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
            category_id = extraction.lookup_category(description)
            extraction.insert_transaction(timestamp, num, description, amount, category_id, account_id)

def discover(account_id, path):
    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            timestamp = int(datetime.strptime(row["Post Date"], "%m/%d/%Y").timestamp())
            description = row["Description"]
            amount = int(float(row["Amount"]) * -100) # Amount is reversed since this is a credit card
            category_id = extraction.lookup_category(description)
            extraction.insert_transaction(timestamp, "", description, amount, category_id, account_id)