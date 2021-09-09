from datetime import timedelta


class ValueDateCalculator:
    __DEFAULT_WEEKENDS = [6, 7]
    __DEFAULT_HOLIDAYS = []
    __ONE_DAY = timedelta(days=1)
    __DEFAULT_SPOT_LAG = timedelta(days=2)
    __TWO_DAYS = timedelta(days=2)

    def __init__(self):
        self.__weekends = {}
        self.__holidays = {}


    def spot_for(self, ccy1, ccy2, trade_date):
        result = trade_date + self.__DEFAULT_SPOT_LAG
        weekends = self.__weekends.get(ccy1, self.__DEFAULT_WEEKENDS)
        usd_holidays = self.__holidays.get('USD', self.__DEFAULT_HOLIDAYS)

        while result.isoweekday() in weekends or result in usd_holidays:
            result += self.__ONE_DAY

        return result


    def set_holidays(self, ccy, holidays):
        self.__holidays[ccy] = holidays


    def set_weekends(self, ccy1, weekends):
        self.__weekends[ccy1] = weekends
