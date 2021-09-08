from datetime import date
from hypothesis import given
from hypothesis.strategies import dates

import settler as s

@given(dates(date(2000, 1, 1), date(2050, 12, 31)))
def test_spot_date_never_falls_on_weekend(trade_date):
    assert s.spot(trade_date).isoweekday() < 6
