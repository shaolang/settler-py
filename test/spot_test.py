from datetime import date, timedelta
from hypothesis import given

import hypothesis.strategies as st
import settler as s

# -- generators --

def trade_dates():
    return st.dates(date(2000, 1, 1), date(2050, 12, 31))


@st.composite
def trade_dates_and_usd_holidays(draw):
    trade_date = draw(trade_dates())
    days_to_add = draw(st.lists(st.integers(0, 20).map(lambda n: trade_date + timedelta(days=n))))

    return (trade_date, days_to_add)

def weekend_lists():
    return st.lists(st.integers(1, 7), max_size=3, unique=True)

# -- properties --

@given(trade_dates())
def test_spot_date_never_falls_on_weekend(trade_date):
    assert s.spot(trade_date).isoweekday() < 6


@given(weekend_lists(), trade_dates())
def test_weekends_arent_always_sat_and_sun_only(weekends, trade_date):
    assert s.spot(trade_date, weekends).isoweekday() not in weekends


@given(trade_dates_and_usd_holidays())
def test_spot_never_falls_on_usd_holidays(trade_date_and_usd_holidays):
    trade_date, usd_holidays = trade_date_and_usd_holidays
    assert s.spot(trade_date, usd_holidays=usd_holidays) not in usd_holidays
