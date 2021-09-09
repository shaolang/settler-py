from datetime import date, timedelta
from hypothesis import given

import hypothesis.strategies as st
import settler as s

# -- generators --

def currency_pairs():
    gen_ccy = st.one_of(
            st.lists(st.characters(min_codepoint=48, max_codepoint=91),
                min_size=3, max_size=3).map(lambda cs: ''.join(cs)),
            st.sampled_from(['USD', 'AUD', 'JPY', 'SGD']))

    return st.lists(gen_ccy, min_size=2, max_size=2, unique=True)


def trade_dates():
    return st.dates(date(2000, 1, 1), date(2050, 12, 31))


@st.composite
def trade_dates_and_usd_holidays(draw):
    trade_date = draw(trade_dates())
    days_to_add = draw(
            st.lists(st.integers(0, 20)
                .map(lambda n: trade_date + timedelta(days=n))))

    return (trade_date, days_to_add)


def weekend_lists():
    return st.lists(st.integers(1, 7), max_size=3, unique=True)

# -- properties --

@given(trade_dates(), currency_pairs())
def test_spot_date_never_falls_on_weekend(trade_date, pair):
    calculator = s.ValueDateCalculator()
    ccy1, ccy2 = pair

    assert calculator.spot_for(ccy1, ccy2, trade_date).isoweekday() < 6


@given(weekend_lists(), trade_dates(), currency_pairs())
def test_weekends_arent_always_sat_and_sun_only(weekends, trade_date, pair):
    ccy1, ccy2 = pair
    calculator = s.ValueDateCalculator()
    calculator.set_weekends(ccy1, weekends)

    assert calculator.spot_for(ccy1, ccy2, trade_date).isoweekday() not in weekends


@given(trade_dates_and_usd_holidays(), currency_pairs())
def test_spot_never_falls_on_usd_holidays(trade_date_and_usd_holidays, pair):
    trade_date, usd_holidays = trade_date_and_usd_holidays
    ccy = pair[1] if pair[0] == 'USD' else pair[0]
    calculator = s.ValueDateCalculator()
    calculator.set_holidays('USD', usd_holidays)

    assert calculator.spot_for(ccy, 'USD', trade_date) not in usd_holidays
