"""
File with methods for calculating return from investment strategies in the past
Different classes - different investment strategies
"""
from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np
import pandas as pd
from pathlib import Path
import json
import os
import datetime as dt

import interface
import stockPrice
import interface.decorators as d

if TYPE_CHECKING:
    from interface import dateType


class StrategyUtils:
    """
    Utilities helpful in backtesting
    """

    @staticmethod
    def loadCriteria(strategyName: str) -> pd.DataFrame:
        """
        Load criteria for specified strategy.
        :param strategyName: strategy's name, the same as file name
        :return:
        """

        folderPath = Path(f"input/stretegysCriteria/")
        filePath = folderPath / f"{strategyName}.json"
        try:
            with open(filePath, 'r') as f:
                criteria = json.load(f)[0]
        except FileNotFoundError:
            raise FileNotFoundError(f"There is no strategy criteria for: {strategyName}. "
                                    f"Exisitings strategies include: {os.listdir(folderPath)}")

        # change criteria to dataframe
        criteria['buyOn'] = pd.DataFrame.from_dict(criteria['buyOn'])
        criteria['sellOn'] = pd.DataFrame.from_dict(criteria['sellOn'])

        return criteria

    @staticmethod
    def loadOperations() -> dict:
        """
        Return dict of operations, where each operation function is assigned to its name.
        :return: dictionary
        """
        operations = {
            ">": np.greater,
            ">=": np.greater_equal,
            "=": np.equal,
            "<=": np.less_equal,
            "<": np.less,
            "!=": np.not_equal,
            "inRange": StrategyUtils.isInRange
        }

        return operations

    @staticmethod
    def isInRange(values: pd.Series, valuesRange: pd.DataFrame) -> pd.Series:
        """
        Checks which elements are in range
        :return: pandas Series with True element which where in range
        """
        return pd.DataFrame({"range1": np.greater(values.values.reshape(-1), valuesRange.iloc[:, 0]),
                            "range2": np.less(values.values.reshape(-1), valuesRange.iloc[:, 1])}).all(axis=1).values




class Strategy(stockPrice.StockPrice):
    """
    Class representing strategy based on buying after stock:
        - is in uptrend (over SMA5 and SMA15)
        - made new high and came back near SMA5
        - buy signal when new high is broken
    """
    def __init__(self, stockPrice: pd.DataFrame, criteria: pd.DataFrame):
        """
        :param stockPrice: stock price data frame
        :param criteria: dictionary with criteria for buying/selling
        """
        super().__init__(stockPrice)
        self.criteria = criteria
        self.operations = StrategyUtils.loadOperations()
        self.firstBuyIdx = 0
        self.firstSellIdx = 0

    def getSP(self):
        return super().getSP()

    def executeTrades(self, startDate: dateType = '', endDate: dateType = ''):
        """
        Runs backtesting for strategy: new high after reversal. Adds to stockPrice dataframe boolean
        columns Buy and Sell. True in these columns means that in these point in time stock should
        be bought/sold. Criteria should be a dictionary that consists of at least two keys:
        ['buyOn', 'sellOn'], values assigned to those keys are data frames with criteria, when all
        of them are fulfilled than a sign to buy/sell is added.
        :param criteria:
        :param startDate:
        :param endDate:
        :return: self
        """
        super().applyDateRange(startDate, endDate)
        self.stockPrice = self.applyBuyCriteria(self.criteria['buyOn'], self.stockPrice)
        strategySignals = self.stockPrice.copy()
        trades = []

        while True in strategySignals["Buy"].values:
            self.firstBuyIdx = self.getFirstBuyIndex(strategySignals)
            strategySignals = strategySignals.loc[self.firstBuyIdx:, :]
            strategySignals = self.applySellCriteria(self.criteria["sellOn"], strategySignals)
            try:
                self.firstSellIdx = self.getFirstSellIndex(strategySignals)
            except IndexError:
                self.firstSellIdx = strategySignals.index[0]
            finally:
                if self.firstBuyIdx == self.firstSellIdx:
                    strategySignals = strategySignals.iloc[1:, :]
                    continue
                trades.append(stockPrice.Trade(self.firstBuyIdx, self.firstSellIdx, strategySignals))
            strategySignals = strategySignals.loc[self.firstSellIdx:, :]
            strategySignals = self.applyBuyCriteria(self.criteria["buyOn"], strategySignals)

        return trades

    def applyBuyCriteria(self, criteria: pd.DataFrame, stockData: pd.DataFrame):
        """
        Adds column Buy which has value True in rows where strategy signal is to buy
        :param criteria:
        :return: self
        """
        if criteria.empty:
            return
        buyOn = pd.DataFrame()

        for c in criteria.iterrows():
            name = c[1].at['statistic']
            operation = c[1].at['operation']
            valueOriginal = c[1].at['value']
            value = self.calculateValue(valueOriginal, stockData)

            # call correct operation function
            columnToCheck = pd.DataFrame(stockData.loc[:, name])
            columnChecked = self.operations[operation](columnToCheck.values, value.values)
            columnChecked = pd.DataFrame(columnChecked,
                                         index=stockData.index,
                                         columns=[f"{name}_{operation}_{valueOriginal}"])
            buyOn = pd.concat([buyOn, columnChecked], axis=1)
            if f"{name}_{operation}_{valueOriginal}" in stockData.columns:
                stockData = stockData.drop(columns=[f"{name}_{operation}_{valueOriginal}"])
        buy = buyOn.all(axis=1).rename("Buy")
        stockData = stockData.drop(columns=["Buy"]) if "Buy" in stockData.columns else stockData

        return pd.concat([stockData, buyOn, buy], axis=1)

    def applySellCriteria(self, criteria: pd.DataFrame, stockData: pd.DataFrame):
        """
        Adds column Sell which has value True in rows where strategy signal is to sell
        :param criteria:
        :param stockData:
        :return: self
        """
        if criteria.empty:
            return
        sellOn = pd.DataFrame()

        for c in criteria.iterrows():
            name = c[1].at['statistic']
            operation = c[1].at['operation']
            valueOriginal = c[1].at['value']
            value = self.calculateValue(valueOriginal, stockData)

            # call correct operation function
            columnToCheck = pd.DataFrame(stockData.loc[:, name])
            columnChecked = self.operations[operation](columnToCheck.values, value.values)
            columnName = f"{name}_{operation}_{valueOriginal}"
            columnChecked = pd.DataFrame(columnChecked,
                                         index=stockData.index,
                                         columns=[columnName])

            sellOn = pd.concat([sellOn, columnChecked], axis=1)
            if columnName in stockData.columns:
                stockData = stockData.drop(columns=[columnName])

        sell = sellOn.any(axis=1).rename("Sell")
        stockData = stockData.drop(columns=["Sell"]) if "Sell" in stockData.columns else stockData

        return pd.concat([stockData, sellOn, sell], axis=1)

    def getFirstBuyIndex(self, strategySignals: pd.DataFrame):
        """
        Returns first index where 'Buy' column is True
        :return:
        """
        return strategySignals.loc[strategySignals["Buy"] == True].index[0]

    def getFirstSellIndex(self, strategySignals: pd.DataFrame):
        """
        Returns first index where 'Buy' column is True
        :return:
        """
        if isinstance(strategySignals, pd.DataFrame) and "Sell" in strategySignals.columns:
            return strategySignals.loc[strategySignals["Sell"] == True].index[0]
        elif isinstance(strategySignals, pd.Series):
            return strategySignals.loc[strategySignals == True].index[0]

    def calculateValue(self, value: (str | int | float), stockPrice: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """
        Calculates value represented in config. Value can be either:
        - simple value (int/float e.g. 1 or 23.81)
        - column name (column that exists in dataframe)
        - math operation (value is calculate based on provided math operation)
          if it's a math operation, it has to follow naming convention: mathOperation:x
          where x is parameter
        :return: column with value
        """
        column = kwargs.pop('column', 'Close')
        valueCalculations = {
            "avg": self.average,
            "max": self.maxLast,
            "min": self.minLast,
            "SL": self.stopLoss,
            "TP": self.takeProfit
        }
        valueColumns = pd.DataFrame(index=stockPrice.index)
        values = value.replace('[', '').replace(']', '').split(':')

        for v in values:
            if isinstance(v, (int | float)) or interface.Utils.isFloat(v):
                valueColumns = pd.concat([valueColumns, pd.Series(float(v), index=stockPrice.index)],
                                         axis=1)
            elif isinstance(v, str) and v in stockPrice.columns:
                valueColumns = pd.concat([valueColumns, stockPrice[v]],
                                         axis=1)
            else:
                calculation = valueCalculations[v.split('_')[0]]
                param = int(v.split('_')[1])
                inputCol = stockPrice[column]
                valueColumns = pd.concat([valueColumns, pd.Series(calculation(inputCol, param), index=stockPrice.index)],
                                         axis=1)

        return valueColumns

    def average(self, inputCol: pd.Series, k: int) -> np.array:
        outputCol = np.repeat(np.nan, k)
        outputCol = np.append(outputCol, [np.mean(inputCol[i-k: i]) for i in range(k, len(inputCol))])
        return outputCol

    def minLast(self, inputCol: pd.Series, k: int) -> np.array:
        k = min(k, inputCol.shape[0])  # prevents returning outputColumn longer than left stockPrice
        outputCol = np.repeat(np.nan, k)
        outputCol = np.append(outputCol, [np.min(inputCol[i-k: i]) for i in range(k, len(inputCol))])
        return outputCol

    def maxLast(self, inputCol: pd.Series, k: int) -> np.array:
        k = min(k, inputCol.shape[0])  # prevents returning outputColumn longer than left stockPrice
        outputCol = np.repeat(np.nan, k)
        outputCol = np.append(outputCol, [np.max(inputCol[i-k: i]) for i in range(k, len(inputCol))])
        return outputCol

    def stopLoss(self, inputCol: pd.Series, k: int) -> np.array:
        # get entry price (next candle's open after buy signal)
        exitPrice = inputCol.iat[0] - k / 10000
        outputCol = np.repeat(exitPrice, len(inputCol.index))
        return outputCol

    def takeProfit(self, inputCol: pd.Series, k: int) -> np.array:
        exitPrice = inputCol.iat[1] + k / 10000
        outputCol = np.repeat(exitPrice, len(inputCol.index))
        return outputCol

