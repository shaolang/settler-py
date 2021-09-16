from datetime import date, timedelta
import hypothesis.strategies as st

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

