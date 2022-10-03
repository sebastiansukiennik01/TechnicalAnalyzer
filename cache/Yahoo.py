"""
File containing classes and methods to interact with Yahoo's API.
"""
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

    def getSP(self):
        return self.stockPrice

    def downloadData(self) -> None:
        """
        Makes API requests and saves ticker data locally.
        :return:
        """
        today = dt.datetime.today().strftime("%Y-%m-%d")
        twoMonthsAgo = (dt.datetime.today() - dt.timedelta(weeks=8)).strftime("%Y-%m-%d")
        correctIntervals = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]

        if self.interval not in correctIntervals:
            raise AttributeError(
                f"Provided interval: {self.interval} is not supported. Please choose one from: {correctIntervals}"
            )

        # create file directory for new time frame
        if not os.path.exists(f"data/forex/{self.interval}/"):
            os.mkdir(f"data/forex/{self.interval}/")

        tickerData = yf.download(self.ticker, start=twoMonthsAgo, end=today, interval=self.interval)
        tickers = self.ticker.split(' ')

        if len(tickers) == 1:
            tickerData.index.tz_convert('Europe/Berlin')
            tickerData.to_csv(f"data/forex/{self.interval}/{self.ticker}.csv")
        else:
            for t in tickers:
                tData = tickerData.loc[:, (slice(None), t)].droplevel([1], axis=1)
                tData.index = tData.index.tz_convert('Europe/Warsaw')
                tData.to_csv(f"data/forex/{self.interval}/{t}.csv")

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
            self.stockPrice = pd.read_csv(filePath, index_col=[0], parse_dates=[0])
        except FileNotFoundError:
            self.ticker = ticker
            self.interval = interval
            self.downloadData()
        finally:
            self.stockPrice = pd.read_csv(filePath, index_col=[0], parse_dates=[0])

        # apply date range
        self.stockPrice = stockPrice.StockPrice(self.stockPrice).applyDateRange(starDate, endDate)

        return self.stockPrice

    def updateExistingIntradayData(self, ticker):
        # if ticker not provided updates all files cached
        pass
