from datetime import timedelta

ONE_DAY = timedelta(days=1)
TWO_DAYS = timedelta(days=2)

def spot(trade_date, weekends=[6, 7]):
    result = trade_date + TWO_DAYS

    while result.isoweekday() in weekends:
        result += ONE_DAY

    return result
