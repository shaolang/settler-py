from datetime import date, timedelta
from hypothesis import given
from random import shuffle

import hypothesis.strategies as st
import settler as s

# -- generators --

def currencies():
    return st.one_of(
            st.lists(st.characters(min_codepoint=48, max_codepoint=91),
                min_size=3, max_size=3).map(lambda cs: ''.join(cs)),
            st.sampled_from(['AUD', 'JPY', 'SGD', 'USD']))


def currency_pairs():
    return st.lists(currencies(), min_size=2, max_size=2, unique=True)


def holidays(trade_date):
    return st.sets(st.integers(0, 20)).map(
            lambda ns: [trade_date + timedelta(days=n) for n in ns])


def spot_lags():
    return st.integers(1, 3)


def trade_dates():
    return st.dates(date(2000, 1, 1), date(2050, 12, 31))


def weekend_lists():
    return st.lists(st.integers(1, 7), max_size=3, unique=True)

# -- property-based tests --

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


@given(currencies(),
        trade_dates().flatmap(lambda d: st.tuples(st.just(d), holidays(d))))
def test_spot_never_falls_on_usd_holidays(ccy, dates):
    trade_date, usd_holidays = dates
    calculator = s.ValueDateCalculator()
    calculator.set_holidays('USD', usd_holidays)

    assert calculator.spot_for(ccy, 'USD', trade_date) not in usd_holidays


@given(currency_pairs(),
        trade_dates().flatmap(
            lambda d: st.tuples(st.just(d), holidays(d), holidays(d))))
def test_spot_never_falls_on_currency_holidays(pair, dates):
    ccy1, ccy2 = pair
    trade_date, holidays1, holidays2 = dates

    calculator = s.ValueDateCalculator()
    calculator.set_holidays(ccy1, holidays1)
    calculator.set_holidays(ccy2, holidays2)

    all_holidays = set(holidays1) | set(holidays2)

    assert calculator.spot_for(ccy1, ccy2, trade_date) not in all_holidays


@given(currency_pairs(), trade_dates(), spot_lags())
def test_same_no_of_biz_days_for_given_spot_lag(pair, trade_date, spot_lag):
    calc = s.ValueDateCalculator()
    calc.set_spot_lag(*pair, spot_lag)

    shuffle(pair)
    spot_date = calc.spot_for(*pair, trade_date)
    total_days = (spot_date - trade_date).days
    total_weekdays = sum(
            [1 for n in range(total_days)
                if (trade_date + timedelta(days=n+1)).isoweekday() < 6])

    assert total_weekdays == spot_lag



# -- example-based tests --

def test_usd_and_currency_holidays_where_usd_holiday_in_between_ccy_holiday():
    trade_date = date(2021, 11, 1)          # Mon

    calc = s.ValueDateCalculator()
    calc.set_holidays('JPY', [date(2021, 11, 2)])    # Tue
    calc.set_holidays('USD', [date(2021, 11, 3)])    # Wed
    calc.set_holidays('SGD', [date(2021, 11, 4)])    # Thu

    assert calc.spot_for('JPY', 'SGD', trade_date) == date(2021, 11, 5)


def test_usd_and_currency_holidays_where_usd_holiday_is_on_candidate_date():
    trade_date = date(2021, 11, 1)          # Mon

    calc = s.ValueDateCalculator()
    calc.set_holidays('JPY', [date(2021, 11, 2)])    # Tue
    calc.set_holidays('USD', [date(2021, 11, 4)])    # Wed

    assert calc.spot_for('JPY', 'SGD', trade_date) == date(2021, 11, 5)


def test_usd_on_t_plus_one_is_counted_as_good_date():
    trade_date = date(2021, 11, 1)  # Mon
    calc = s.ValueDateCalculator()

    calc.set_holidays('USD', [date(2021, 11, 2)])   # Tue
    pair = ['USD', 'SGD']
    shuffle(pair)

    assert calc.spot_for(*pair, trade_date) == date(2021, 11, 3)


def test_defaults_sat_and_sun_as_weekends():
    trade_date = date(2021, 11, 5)  # Fri
    calc = s.ValueDateCalculator()

    assert calc.spot_for('ABC', 'XYZ', trade_date) == date(2021, 11, 9) # Tue
