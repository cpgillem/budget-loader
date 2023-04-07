from dateutil import relativedelta
from datetime import datetime, date, time

def to_dollars(cents):
    if cents is None:
        return 0
    else:
        return cents / 100

# Get start and end dates.
def get_start_end(year, month):
    start = datetime.combine(date(year, month, 1), time(0, 0))
    dt = relativedelta.relativedelta(months=1) # Add a month
    end = start + dt
    return (start, end)