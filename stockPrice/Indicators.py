"""
File containing methods for calculating indicator values over time series
"""
import pandas as pd
import ta


class Indicators(object):

    @staticmethod
    def SMA(stockPrice: pd.DataFrame, column: str = "close") -> pd.DataFrame:
        sma = ta.add_trend_ta(stockPrice, high='High', low='Low', close='Close', fillna=True)
        print(sma.head())

    def EMA(self, stockPrice: pd.DataFrame, column: str = "close") -> pd.DataFrame:
        pass

    def RSI(self, stockPrice: pd.DataFrame) -> pd.DataFrame:
        pass

    def MACD(self, stockPrice: pd.DataFrame) -> pd.DataFrame:
        pass
