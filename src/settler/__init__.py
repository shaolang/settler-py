from datetime import timedelta

ONE_DAY = timedelta(days=1)
TWO_DAYS = timedelta(days=2)

def spot(trade_date, weekends=[6, 7], *, usd_holidays=[]):
    result = trade_date + TWO_DAYS

    while result.isoweekday() in weekends or result in usd_holidays:
        result += ONE_DAY

    return result
