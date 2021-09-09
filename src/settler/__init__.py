from datetime import timedelta
from itertools import islice


class ValueDateCalculator:
    __DEFAULT_WEEKENDS = [6, 7]
    __DEFAULT_HOLIDAYS = []
    __ONE_DAY = timedelta(days=1)

    def __init__(self):
        self.__weekends = {}
        self.__holidays = {}


    def set_holidays(self, ccy, holidays):
        self.__holidays[ccy] = holidays


    def set_weekends(self, ccy1, weekends):
        self.__weekends[ccy1] = weekends


    def spot_for(self, ccy1, ccy2, trade_date):
        ccy1_pred = self.__biz_day_predicate(ccy1)
        ccy2_pred = self.__biz_day_predicate(ccy2)
        ccy1_dates = self.__biz_dates(trade_date, ccy1_pred)
        ccy2_dates = self.__biz_dates(trade_date, ccy2_pred)
        ccy1_spot = list(islice(ccy1_dates, 2))[-1]
        ccy2_spot = list(islice(ccy2_dates, 2))[-1]
        candidate = ccy1_spot if ccy1_spot > ccy2_spot else ccy2_spot

        pair_pred = lambda d: ccy1_pred(d) and ccy2_pred(d)

        if not pair_pred(candidate):
            candidate = next(self.__biz_dates(candidate, pair_pred))

        return candidate


    def __biz_day_predicate(self, ccy):
        weekends = self.__weekends.get(ccy,self. __DEFAULT_WEEKENDS)
        holidays = self.__holidays.get(ccy,self. __DEFAULT_HOLIDAYS)

        return lambda d: d.isoweekday() not in weekends and d not in holidays


    def __biz_dates(self, trade_date, is_biz_day):
        result = trade_date + self.__ONE_DAY

        while True:
            if is_biz_day(result):
                yield result
            result += self.__ONE_DAY
