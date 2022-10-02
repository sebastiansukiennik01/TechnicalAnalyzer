"""
File containing classes and methods to perform operation over stock prices.
"""
import datetime as dt
import pandas as pd
from dateutil.relativedelta import relativedelta


""" Custom data types """
dateType = (str | dt.datetime | pd.DatetimeIndex)


class StockPrice(object):

    def __init__(self, stockPrice: pd.DataFrame):
        self.stockPrice = stockPrice

    def getSP(self):
        return self.stockPrice

    def applyDateRange(self, startDate: dateType = '', endDate: dateType = '') -> pd.DataFrame:
        """
        Applies provided date range. Truncates stock price dataframe to only those that are from [startDate:endDate]
        period.
        :param startDate: date form which to extract data
        :param endDate: to which to extract data
        :return: Data from selected data range.
        """

        startDate, endDate = self.interpretDates(startDate, endDate)

        if startDate == '':
            startDate = self.stockPrice.index[0]
        if endDate == '':
            endDate = self.stockPrice.index[-1]

        # format to datetime if start/end is still string
        startDate = pd.to_datetime(startDate, utc=True)
        endDate = pd.to_datetime(endDate, utc=True)

        self.stockPrice = self.stockPrice.loc[startDate:endDate, :]

        return self.stockPrice

    def interpretDates(self, startDate: dateType = '', endDate: dateType = '') -> (dt.datetime, dt.datetime):
        """
        Interprets dats from short encoded to datetime. E.g. Y-1 represents today's date from one year before,
        W-2 as startDate will correspond to Monday (Friday if provided as endDate) of previous to last week and
        H-1 will return datetime from one hour before
        :param startDate: encoded start date
        :param endDate: encoded end date
        :return: tuple of dates in datetime format
        """
        # check if provided encoded date format is supported
        correctPrefix = ["Y-", "W-", "H-"]
        if startDate and startDate[:2] not in correctPrefix:
            raise AttributeError(f"Provide encoded start date is incorrect. Choose one from {correctPrefix} and try again")
        if endDate and endDate[:2] not in correctPrefix:
            raise AttributeError(f"Provide encoded start date is incorrect. Choose one from {correctPrefix} and try again")

        start, end = startDate, endDate

        # for H-k
        now = dt.datetime.now().replace(microsecond=0)
        if "H-" in startDate:
            hours = int(startDate[2:])
            start = now - relativedelta(hours=hours, minutes=now.time().minute, seconds=now.time().second)
        if "H-" in endDate:
            hours = int(endDate[2:]) - 1
            end = now - relativedelta(hours=hours, minutes=now.time().minute, seconds=now.time().second)

        # for W-k
        today = dt.datetime.today().replace(microsecond=0)
        if "W-" in startDate:
            weeks = int(startDate.replace('W', '').replace('-', ''))
            start = today.date() - relativedelta(days=+today.weekday(), weeks=weeks)
        elif "W+" in startDate:
            weeks = int(startDate.replace('W', '').replace('+', ''))
            start = today.date() - relativedelta(days=+today.weekday()) + relativedelta(weeks=weeks)

        if "W-" in endDate:
            weeks = int(endDate.replace('W', '').replace('-', ''))
            end = today.date() - relativedelta(days=+today.weekday()-4, weeks=weeks)
        elif "W+" in endDate:
            weeks = int(endDate.replace('W', '').replace('+', ''))
            end = today.date() - relativedelta(days=+today.weekday()-4) + relativedelta(weeks=weeks)

        # for Y-k
        if "Y" in startDate:
            start = today.date() - relativedelta(years=int(startDate.replace('Y', '').replace('-', '')))
        if "Y" in endDate:
            end = today.date() - relativedelta(years=int(endDate.replace('Y', '').replace('-', '')))

        return start, end

