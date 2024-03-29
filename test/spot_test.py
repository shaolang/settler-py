from datetime import date, timedelta
from . import generators as g
from hypothesis import given
from random import shuffle

import hypothesis.strategies as st
import settler as s

# -- property-based tests --

@given(g.trade_dates(), g.currency_pairs())
def test_spot_date_never_falls_on_weekend(trade_date, pair):
    calculator = s.ValueDateCalculator()
    ccy1, ccy2 = pair

    assert calculator.spot_for(f'{ccy1}{ccy2}', trade_date).isoweekday() < 6


@given(g.weekend_lists(), g.trade_dates(), g.currency_pairs())
def test_weekends_arent_always_sat_and_sun_only(weekends, trade_date, pair):
    ccy1, _ = pair
    calculator = s.ValueDateCalculator()
    calculator.set_weekends(ccy1, weekends)

    assert calculator.spot_for(''.join(pair), trade_date).isoweekday() not in weekends


@given(g.currencies(),
        g.trade_dates().flatmap(lambda d: st.tuples(st.just(d), g.holidays(d))))
def test_spot_never_falls_on_usd_holidays(ccy, dates):
    trade_date, usd_holidays = dates
    calculator = s.ValueDateCalculator()
    calculator.set_holidays('USD', usd_holidays)

    assert calculator.spot_for(f'{ccy}USD', trade_date) not in usd_holidays


@given(g.currency_pairs(),
        g.trade_dates().flatmap(
            lambda d: st.tuples(st.just(d), g.holidays(d), g.holidays(d))))
def test_spot_never_falls_on_currency_holidays(pair, dates):
    ccy1, ccy2 = pair
    trade_date, holidays1, holidays2 = dates

    calculator = s.ValueDateCalculator()
    calculator.set_holidays(ccy1, holidays1)
    calculator.set_holidays(ccy2, holidays2)

    all_holidays = set(holidays1) | set(holidays2)

    assert calculator.spot_for(''.join(pair), trade_date) not in all_holidays


@given(g.currency_pairs(), g.trade_dates(), g.spot_lags())
def test_same_no_of_biz_days_for_given_spot_lag(pair, trade_date, spot_lag):
    calc = s.ValueDateCalculator()
    calc.set_spot_lag(''.join(pair), spot_lag)

    shuffle(pair)
    spot_date = calc.spot_for(''.join(pair), trade_date)
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

    assert calc.spot_for('JPYSGD', trade_date) == date(2021, 11, 5)


def test_usd_and_currency_holidays_where_usd_holiday_is_on_candidate_date():
    trade_date = date(2021, 11, 1)          # Mon

    calc = s.ValueDateCalculator()
    calc.set_holidays('JPY', [date(2021, 11, 2)])    # Tue
    calc.set_holidays('USD', [date(2021, 11, 4)])    # Wed

    assert calc.spot_for('JPYSGD', trade_date) == date(2021, 11, 5)


def test_usd_on_t_plus_one_is_counted_as_good_date():
    trade_date = date(2021, 11, 1)  # Mon
    calc = s.ValueDateCalculator()

    calc.set_holidays('USD', [date(2021, 11, 2)])   # Tue
    pair = ['USD', 'SGD']
    shuffle(pair)
    ccy1, ccy2 = pair

    assert calc.spot_for(f'{ccy1}{ccy2}', trade_date) == date(2021, 11, 3)


def test_defaults_sat_and_sun_as_weekends():
    trade_date = date(2021, 11, 5)  # Fri
    calc = s.ValueDateCalculator()

    assert calc.spot_for('ABCXYZ', trade_date) == date(2021, 11, 9) # Tue
