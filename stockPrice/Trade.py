"""
Contains class representing single trade.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

import pandas as pd
import datetime as dt

if TYPE_CHECKING:
    from interface import dateType


class Trade:

    def __init__(self,
                 entryDate: dateType,
                 exitDate: dateType,
                 stockPrice: pd.DataFrame,
                 profitType: str = "t",
                 takeProfit: (float | int) = 30,
                 stopLoss: (float | int) = 30):
        """
        :param entryDate: opening trade date
        :param exitDate: closing trade date
        :param stockPrice: dataframe with stock price
        :param profitType: 'r' for real/'t' for theoretical
        """
        self.entryDate: dateType = entryDate
        self.exitDate: dateType = exitDate
        self.stockPriceDuringTrade = stockPrice.loc[entryDate:exitDate, ["Open", "High", "Low", "Close"]]
        self.profitType = profitType
        self.takeProfit = takeProfit
        self.stopLoss = stopLoss
        self.duration: dateType = self.setDuration()
        self.profit: float = self.setProfit()

    def setProfit(self):
        assert self.profitType in ['r', 't']
        entryClose = self.stockPriceDuringTrade.at[self.entryDate, "Close"]
        exitHigh = self.stockPriceDuringTrade.at[self.exitDate, "High"]
        exitLow = self.stockPriceDuringTrade.at[self.exitDate, "Open"]

        if exitHigh > entryClose:
            return round(exitHigh - entryClose, 4) if self.profitType == 'r' else self.takeProfit/10000
        else:
            return round(exitLow - entryClose, 4) if self.profitType == 'r' else -self.stopLoss/10000

    def setDuration(self):
        if isinstance(self.entryDate, str):
            self.entryDate = dt.datetime.strptime(self.entryDate, "%Y-%m-%d %H:%M:%S")
        if isinstance(self.exitDate, str):
            self.exitDate = dt.datetime.strptime(self.exitDate, "%Y-%m-%d %H:%M:%S")

        return self.exitDate - self.entryDate
