from datetime import date
from hypothesis import given

import hypothesis.strategies as st
import settler as s

# -- generators --

def trade_dates():
    return st.dates(date(2000, 1, 1), date(2050, 12, 31))

def weekend_lists():
    return st.lists(st.integers(1, 7), max_size=3, unique=True)

# -- properties --

@given(trade_dates())
def test_spot_date_never_falls_on_weekend(trade_date):
    assert s.spot(trade_date).isoweekday() < 6


@given(weekend_lists(), trade_dates())
def test_weekends_arent_always_sat_and_sun_only(weekends, trade_date):
    assert s.spot(trade_date, weekends).isoweekday() not in weekends
