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


import stockPrice

if TYPE_CHECKING:
    from interface import dateType


class Utils:
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
            "!=": np.not_equal
        }

        return operations


    @staticmethod
    def calculateValue(value: (str | int | float), stockPrice: pd.DataFrame, **kwargs) -> pd.Series:
        """
        Calculates value represented in config. Value can be either:
        - simple value (int/float e.g. 1 or 23.81)
        - column name (column that exists in dataframe)
        - math operation (value is calculate based on provided math operation)
          if it's a math operation, it has to follow naming convention: mathOperation:x
          where x is parameter
        :return: column with value
        """
        valueCalculations = {
            "avg": Utils.average,
            "max": Utils.maxLast,
            "min": Utils.minLast
        }
        column = kwargs.pop('column', 'Close')

        if isinstance(value, (int | float)):
            return pd.Series(value, index=stockPrice.index)
        elif isinstance(value, str) and value in stockPrice.columns:
            return stockPrice[value]
        else:
            calculation = valueCalculations[value.split(':')[0]]
            param = int(value.split(':')[1])
            inputCol = stockPrice[column]
            return pd.Series(calculation(inputCol, param), index=stockPrice.index)

    @staticmethod
    def average(inputCol: pd.Series, k: int) -> np.array:
        outputCol = np.repeat(np.nan, k)
        outputCol = np.append(outputCol, [np.mean(inputCol[i-k: i]) for i in range(k, len(inputCol))])
        return outputCol

    @staticmethod
    def minLast(inputCol: pd.Series, k: int) -> np.array:
        outputCol = np.repeat(np.nan, k)
        outputCol = np.append(outputCol, [np.min(inputCol[i-k: i]) for i in range(k, len(inputCol))])
        return outputCol

    @staticmethod
    def maxLast(inputCol: pd.Series, k: int) -> np.array:
        outputCol = np.repeat(np.nan, k)
        outputCol = np.append(outputCol, [np.max(inputCol[i-k: i]) for i in range(k, len(inputCol))])
        return outputCol


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
        self.operations = Utils.loadOperations()

    def getSP(self):
        return super().getSP()

    def run(self, startDate: dateType = '', endDate: dateType = ''):
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
        self.applyBuyCriteria(self.criteria['buyOn'])
        self.applySellCriteria(self.criteria['sellOn'])

        return self

    def applyBuyCriteria(self, criteria: pd.DataFrame):
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
            value = Utils.calculateValue(c[1].at['value'], self.stockPrice)

            # call correct operation function
            columnToCheck = self.stockPrice.loc[:, name]
            result = self.operations[operation](columnToCheck, value)
            columnChecked = pd.DataFrame(result,
                                         index=self.stockPrice.index,
                                         columns=[f"{name}_{operation}_{valueOriginal}"])
            buyOn = pd.concat([buyOn, columnChecked], axis=1)

        buy = buyOn.all(axis=1).rename("Buy")
        self.stockPrice = pd.concat([self.stockPrice, buyOn, buy], axis=1)

    def applySellCriteria(self, criteria: pd.DataFrame):
        """
        Adds column Sell which has value True in rows where strategy signal is to sell
        :param criteria:
        :return: self
        """
        if criteria.empty:
            return
        sellOn = pd.DataFrame()

        for c in criteria.iterrows():
            name = c[1].at['statistic']
            operation = c[1].at['operation']
            valueOriginal = c[1].at['value']
            value = Utils.calculateValue(c[1].at['value'], self.stockPrice)

            # call correct operation function
            columnToCheck = self.stockPrice.loc[:, name]
            columnChecked = self.operations[operation](columnToCheck, value)
            columnChecked = pd.DataFrame(columnChecked,
                                         index=self.stockPrice.index,
                                         columns=[f"{name}_{operation}_{valueOriginal}"])
            sellOn = pd.concat([sellOn, columnChecked], axis=1)

        sell = sellOn.all(axis=1).rename("Sell")
        self.stockPrice = pd.concat([self.stockPrice, sellOn, sell], axis=1)
