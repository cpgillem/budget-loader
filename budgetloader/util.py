from dateutil import relativedelta
from datetime import datetime, date, time

# Convert cents to dollhairs for display purposes.
def to_dollars(cents):
    if cents is None:
        return 0
    else:
        return round(cents / 100, 2)

# Convert to cents for more accurate storage.
def to_cents(dollars):
    if dollars is None:
        return 0
    else:
        return int(float(dollars) * 100)

# Get start and end dates.
def get_start_end(year, month):
    start = datetime.combine(date(year, month, 1), time(0, 0))
    dt = relativedelta.relativedelta(months=1) # Add a month
    end = start + dt
    return (start, end)
