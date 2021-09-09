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


def holidays(trade_date):
    return st.sets(st.integers(0, 20)).map(
            lambda ns: [trade_date + timedelta(days=n) for n in ns])


def trade_dates():
    return st.dates(date(2000, 1, 1), date(2050, 12, 31))


@st.composite
def trade_dates_and_usd_holidays(draw):
    trade_date = draw(trade_dates())
    usd_holidays = draw(holidays(trade_date))

    return (trade_date, usd_holidays)


@st.composite
def trade_date_pair_and_holidays(draw):
    trade_date = draw(trade_dates())
    pair = draw(currency_pairs())
    ccy_holidays = [draw(holidays(trade_date)), draw(holidays(trade_date))]

    return (trade_date, pair, ccy_holidays)


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


@given(trade_date_pair_and_holidays())
def test_spot_never_falls_on_currency_holidays(trade_date_pair_and_holidays):
    trade_date, [ccy1, ccy2], [holidays1, holidays2] = trade_date_pair_and_holidays

    calculator = s.ValueDateCalculator()
    calculator.set_holidays(ccy1, holidays1)
    calculator.set_holidays(ccy2, holidays2)

    all_holidays = set(holidays1) | set(holidays2)

    assert calculator.spot_for(ccy1, ccy2, trade_date) not in all_holidays
