"""
File containing classes and methods to interact with Yahoo's API.
"""
import dateutil.parser
import pandas as pd
import datetime as dt
import yfinance as yf
import os

import stockPrice


pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)



class Yahoo(object):

    def __init__(self, ticker: (str | list), interval: str = "5m"):
        """
        :param ticker: stock price/forex pair code
        :param interval: timeFrame for stock price (e.g. 1min/5min/1h/...)
        """
        self.ticker = " ".join(ticker) if isinstance(ticker, list) else ticker
        self.stockPrice = None
        self.interval = interval
        self.correctIntervals = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]

    def getSP(self):
        return self.stockPrice

    def downloadData(self) -> None:
        """
        Makes API requests and saves ticker data locally.
        :return:
        """
        twoMonthsAgo = (dt.datetime.today() - dt.timedelta(weeks=8)).strftime("%Y-%m-%d")
        twoMonthsAgo = (dt.datetime.today() - dt.timedelta(weeks=1)).strftime("%Y-%m-%d") if "1m" in self.interval else twoMonthsAgo
        maxAvailableStart = self.maxAvailableStartDate()
        print(maxAvailableStart)


        if self.interval not in self.correctIntervals:
            raise AttributeError(
                f"Provided interval: {self.interval} is not supported. "
                f"Please choose one from: {self.correctIntervals}"
            )

        # create file directory for new time frame
        if not os.path.exists(f"data/forex/{self.interval}/"):
            os.mkdir(f"data/forex/{self.interval}/")

        tickerData = yf.download(self.ticker, start=maxAvailableStart, interval=self.interval)
        tickers = self.ticker.split(' ')

        if len(tickers) == 1:
            tickerData.index.tz_localize('Europe/Warsaw')
            self.appendToExistingData(tickerData, f"data/forex/{self.interval}/{self.ticker}.csv")
        else:
            for t in tickers:
                tData = tickerData.loc[:, (slice(None), t)].droplevel([1], axis=1)
                try:
                    tData.index = tData.index.tz_convert('Europe/Warsaw')
                except TypeError:
                    tData.index = tData.index.tz_localize('Europe/Warsaw')
                self.appendToExistingData(tData, f"data/forex/{self.interval}/{t}.csv")

    def loadData(self, ticker: str, **kwargs) -> pd.DataFrame:
        """
        Loads cached stock price data
        :param ticker: stock price/forex pair code
        :return:
        """
        # extract kwargs
        starDate = kwargs.pop('startDate', '')
        endDate = kwargs.pop('endDate', '')
        interval = kwargs.pop('interval', self.interval)

        # check if file with correct timeFrame exists, if not getData than proceed
        try:
            filePath = f"data/forex/{interval}/{ticker}.csv"
            self.interval = interval
            self.stockPrice = pd.read_csv(filePath, index_col=[0], parse_dates=[0])
        except FileNotFoundError:
            self.ticker = ticker
            self.interval = interval
            self.downloadData()
        finally:
            customDateParser = lambda x: dateutil.parser.parse(x, ignoretz=False)
            self.stockPrice = pd.read_csv(filePath, index_col=[0], parse_dates=[0], date_parser=customDateParser)
            try:
                self.stockPrice.index = self.stockPrice.index.tz_convert('Europe/Warsaw')
            except TypeError:
                self.stockPrice.index = self.stockPrice.index.tz_localize('Europe/Warsaw')

        # apply date range
        self.stockPrice = stockPrice.StockPrice(self.stockPrice).applyDateRange(starDate, endDate)

        return self.stockPrice

    def appendToExistingData(self, newData: pd.DataFrame, filePath: str):
        """
        Appends data to cached stockPrice files
        :param newData: latest stock price data frame
        :param filePath: path to file where data should be stored
        :return: None
        """
        if not os.path.exists(filePath):
            newData.to_csv(filePath)
        else:
            ticker = filePath.split("/")[-1].replace(".csv", "")
            try:
                lastFull = newData.index[-4]
            except IndexError:
                lastFull = newData.index[-1]
            oldData = self.loadData(ticker)
            pd.concat([oldData.iloc[:-1, :],
                       newData.loc[oldData.index[-1]:, :]])\
                .dropna()\
                .to_csv(filePath)

    def maxAvailableStartDate(self):
        if self.interval in ["1m"]:
            return dt.datetime.today() - dt.timedelta(days=7) + dt.timedelta(minutes=1)
        elif self.interval in ["2m", "5m", "15m", "30m", "60m", "90m", "1h"]:
            return dt.datetime.today() - dt.timedelta(weeks=8)
        elif self.interval in ["1d", "5d", "1wk", "1mo", "3mo"]:
            return '2000-01-01'
