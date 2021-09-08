from datetime import date
from hypothesis import given

import hypothesis.strategies as st
import settler as s

@given(st.dates(date(2000, 1, 1), date(2050, 12, 31)))
def test_spot_date_never_falls_on_weekend(trade_date):
    assert s.spot(trade_date).isoweekday() < 6
