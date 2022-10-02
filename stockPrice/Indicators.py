"""
File containing methods for calculating indicator values over time series
"""
import pandas as pd
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

from stockPrice.StockPrice import StockPrice


class Indicators(StockPrice):

    def __init__(self, stockPrice: pd.DataFrame):
        super().__init__(stockPrice)

    def getSP(self):
        return super().getSP()

    def addSMA(self, column: (str | list) = "Close", length: int = 20, ) -> pd.DataFrame:
        """
        Adds column with SMA values to provided StockPrice DataFrame. SMA is calculated on values from specified
        column/columns.
        :param column: columns names from which to calculate SMA
        :param length: number of periods used to calculate moving average
        :return: self
        """
        column = [column] if isinstance(column, str) else column
        smaInput = self.stockPrice.loc[:, column]
        for s in smaInput:
            smaOutput = SMAIndicator(smaInput[s], window=length).sma_indicator()
            smaOutput = smaOutput.rename(f"{s}_{smaOutput.name}")
            self.stockPrice = pd.concat([self.stockPrice, smaOutput], axis=1)

        return self

    def addEMA(self, column: (str | list) = "Close", length: int = 10) -> pd.DataFrame:
        """
        Adds column with EMA values to provided StockPrice DataFrame. EMA is calculated on values from specified
        column/columns and with length
        :param column: columns name's from which to calculate EMA
        :param length: number of periods used to calculate moving average
        :return: self
        """
        column = [column] if isinstance(column, str) else column
        emaInput = self.stockPrice.loc[:, column]
        for e in emaInput:
            emaOutput = EMAIndicator(emaInput[e], window=length).ema_indicator()
            emaOutput = emaOutput.rename(f"{e}_{emaOutput.name}")
            self.stockPrice = pd.concat([self.stockPrice, emaOutput], axis=1)

        return self

    def addRSI(self, column: (str | list) = "Close", length: int = 14) -> pd.DataFrame:
        """
        Adds columns with RSI values
        :param column: column from which to calculate RSI
        :param length: number of periods used to calculate RSI (more -> smoother)
        :return: self
        """
        column = [column] if isinstance(column, str) else column
        rsiInput = self.stockPrice.loc[:, column]
        for r in rsiInput:
            rsiOutput = RSIIndicator(rsiInput[r], window=length).rsi()
            rsiOutput = rsiOutput.rename(f"{r}_{rsiOutput.name}")
            self.stockPrice = pd.concat([self.stockPrice, rsiOutput], axis=1)

        return self

    def addMACD(self, column: (str | list) = "Close", **kwargs) -> pd.DataFrame:
        """
        Adds Moving Average Convergence Divergence values
        :return: self
        """
        longMACD = kwargs.pop("longMACD", 26)
        shortMACD = kwargs.pop("shortMACD", 12)
        signalMACD = kwargs.pop("signalMACD", 9)

        if kwargs:
            raise UserWarning(
                f"{kwargs} contains not allowed parameters. Please choose from: [longMACD, shortMACD, signalMACD]"
            )

        column = [column] if isinstance(column, str) else column
        macdInput = self.stockPrice.loc[:, column]
        for m in macdInput:
            macdOutput = MACD(macdInput[m], window_slow=longMACD, window_fast=shortMACD, window_sign=signalMACD)
            macd = macdOutput.macd().rename(f"{m}_{macdOutput.macd().name}")
            macdSignal = macdOutput.macd_signal().rename(f"{m}_{macdOutput.macd_signal().name}")
            macdDiff = macdOutput.macd_diff().rename(f"{m}_{macdOutput.macd_diff().name}")
            self.stockPrice = pd.concat([self.stockPrice, macd, macdSignal, macdDiff], axis=1)

        return self

    def addBollingerBands(self, column: (str | list) = "Close", length: int = 20, sdFactor: int = 2):
        """
        Adds Boligner Bands values to data frame. They represent 'price + sd' and 'price - sd'.
        :return:
        """
        column = [column] if isinstance(column, str) else column
        bbInput = self.stockPrice.loc[:, column]
        for b in bbInput:
            bOutput = BollingerBands(bbInput[b], window=length, window_dev=sdFactor)
            bMid = bOutput.bollinger_mavg().rename(f"{b}_{bOutput.bollinger_mavg()}")
            bHigh = bOutput.bollinger_hband().rename(f"{b}_{bOutput.bollinger_hband()}")
            bLow = bOutput.bollinger_lband().rename(f"{b}_{bOutput.bollinger_lband()}")
            bWidth = bOutput.bollinger_wband().rename(f"{b}_{bOutput.bollinger_wband()}")
            bHighIndic = bOutput.bollinger_hband_indicator().rename(f"{b}_{bOutput.bollinger_hband_indicator()}")
            bLowIndic = bOutput.bollinger_lband_indicator().rename(f"{b}_{bOutput.bollinger_lband_indicator()}")
            self.stockPrice = pd.concat([self.stockPrice, bMid, bLow, bHigh, bWidth, bHighIndic, bLowIndic], axis=1)

        return self
