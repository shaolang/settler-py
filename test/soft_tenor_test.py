from . import generators as gen
from datetime import date
import pytest
import settler as s

# -- example-based tests --

@pytest.mark.parametrize('trade_date,tenor,expected', [
    (date(2021, 11, 1), '1W', date(2021, 11, 10)),
    (date(2021, 11, 1), '1M', date(2021, 12, 3))])
def test_tenors_beyond_spot_starts_from_spot(trade_date, tenor, expected):
    vd = s.ValueDateCalculator()

    assert vd.value_date_for('USD', 'SGD', tenor, trade_date) == expected
