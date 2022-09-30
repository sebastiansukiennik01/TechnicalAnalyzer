"""
File containing classes and methods to interact with Yahoo's API.
"""
import pandas as pd
import datetime as dt
import yfinance as yf
import os

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)


class Yahoo(object):

    def __init__(self, ticker: (str | list), interval: str = "5m"):
        self.ticker = " ".join(ticker) if isinstance(ticker, list) else ticker
        self.stockPrice = None
        self.interval = interval

    def getData(self) -> None:
        """
        Makes API requests and saves ticker data locally.
        :param interval: timeFrame for stock price (e.g. 1min/5min/1h/...)
        :return:
        """
        today = dt.datetime.today().strftime("%Y-%m-%d")
        twoMonthsAgo = (dt.datetime.today() - dt.timedelta(weeks=8)).strftime("%Y-%m-%d")
        correctIntervals = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]

        if self.interval not in correctIntervals:
            raise AttributeError(
                f"Provided interval: {self.interval} is not supported. Please choose one from: {correctIntervals}"
            )

        if not os.path.exists(f"cache/data/forex/{self.interval}/"):
            os.mkdir(f"cache/data/forex/{self.interval}/")

        tickerData = yf.download(self.ticker, start=twoMonthsAgo, end=today, interval=self.interval)
        tickers = self.ticker.split(' ')

        if len(tickers) == 1:
            tickerData.to_csv(f"cache/data/forex/{self.interval}/{self.ticker}.csv")
        else:
            for t in tickers:
                tData = tickerData.loc[:, (slice(None), t)].droplevel([1], axis=1)
                tData.to_csv(f"cache/data/forex/{self.interval}/{t}.csv")

    def loadData(self, ticker: str, startDate: str, endDate: str, timeFrame: str) -> pd.DataFrame:
        """
        Loads cached stock price data.
        :param ticker:
        :param startDate:
        :param endDate:
        :param timeFrame:
        :return:
        """





    def updateExistingIntradaylData(self, ticker):
        pass
