from datetime import timedelta
from itertools import islice


class ValueDateCalculator:
    __DEFAULT_WEEKENDS = [6, 7]
    __DEFAULT_HOLIDAYS = []
    __DEFAULT_SPOT_LAG = 2
    __ONE_DAY = timedelta(days=1)

    def __init__(self):
        self.__weekends = {}
        self.__holidays = {}
        self.__spot_lags = {}


    def set_holidays(self, ccy, holidays):
        self.__holidays[ccy] = holidays


    def set_spot_lag(self, pair, spot_lag):
        self.__spot_lags[tuple(pair)] = spot_lag
        self.__spot_lags[tuple(pair[::-1])] = spot_lag


    def set_weekends(self, ccy1, weekends):
        self.__weekends[ccy1] = weekends


    def spot_for(self, ccy1, ccy2, trade_date):
        spot_lag = self.__spot_lags.get((ccy1, ccy2), self.__DEFAULT_SPOT_LAG)
        ccy1_pred, ccy1_spot = self.__pred_and_spot(ccy1, trade_date, spot_lag)
        ccy2_pred, ccy2_spot = self.__pred_and_spot(ccy2, trade_date, spot_lag)
        candidate = ccy1_spot if ccy1_spot > ccy2_spot else ccy2_spot
        usd_pred = self.__biz_day_predicate('USD', True)

        candidate_pred = lambda d: ccy1_pred(d) and ccy2_pred(d) and usd_pred(d)

        if not candidate_pred(candidate):
            candidate = next(self.__biz_dates(candidate, candidate_pred))

        return candidate


    def __biz_day_predicate(self, ccy, include_holidays):
        weekends = self.__weekends.get(ccy, self.__DEFAULT_WEEKENDS)
        holidays = (
                self.__holidays.get(ccy, self.__DEFAULT_HOLIDAYS)
                if include_holidays
                else [])

        return lambda d: d.isoweekday() not in weekends and d not in holidays


    def __biz_dates(self, trade_date, is_biz_day):
        result = trade_date + self.__ONE_DAY

        while True:
            if is_biz_day(result):
                yield result
            result += self.__ONE_DAY


    def __pred_and_spot(self, ccy, trade_date, spot_lag):
        include_holidays = ccy != 'USD'
        pred = self.__biz_day_predicate(ccy, include_holidays)

        return (pred,
                list(islice(self.__biz_dates(trade_date, pred), spot_lag))[-1])
