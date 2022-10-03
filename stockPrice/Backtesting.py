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


class Utils(object):

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
            "inRange": Utils.isInRange,
        }

        return operations

    @staticmethod
    def isInRange(val, min, max):
        pass


class NewHighAfterReversal(stockPrice.StockPrice):
    
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
        Runs backtesting for strategy: new high after reversal. Adds to stockPrice dataframe boolean columns
        Buy and Sell. True in these columns means that in these point in time stock should be bought/sold.
        Criteria should be a dictionary that consists of at least two keys: ['buyOn', 'sellOn'], values assigned
        to those keys are data frames with criteria, when all of them are fulfilled than a sign to buy/sell is added.
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
            value = self.stockPrice.loc[:, valueOriginal] if isinstance(valueOriginal, str) else valueOriginal

            # call correct operation function
            columnToCheck = self.stockPrice.loc[:, name]
            result = self.operations[operation](columnToCheck, value)
            columnChecked = pd.DataFrame(result, index=self.stockPrice.index, columns=[f"{name}_{operation}_{valueOriginal}"])
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
            value = self.stockPrice.loc[:, valueOriginal].values if isinstance(valueOriginal, str) else valueOriginal

            # call correct operation function
            columnToCheck = self.stockPrice.loc[:, name].values
            columnChecked = self.operations[operation](columnToCheck, value)
            columnChecked = pd.DataFrame(columnChecked, index=self.stockPrice.index, columns=[f"{name}_{operation}_{valueOriginal}"])
            sellOn = pd.concat([sellOn, columnChecked], axis=1)

        sell = sellOn.all(axis=1).rename("Sell")
        self.stockPrice = pd.concat([self.stockPrice, sellOn, sell], axis=1)

