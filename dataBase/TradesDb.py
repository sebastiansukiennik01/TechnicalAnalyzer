"""
File containing methods for connection to databases for Trade class
"""

import pymysql
import sqlalchemy
import pandas as pd

import interface.Utils


class StockPriceDb(object):

    def __init__(self):
        def conn():
            return pymysql.connect(user='root',
                                   password='root12345',
                                   host='127.0.0.1',
                                   database='technical_analyzer')
        self.connection = conn
        self.engine = sqlalchemy.create_engine('mysql+pymysql://', creator=self.connection)

    def findByTickerInterval(self, ticker: str, interval: str) -> pd.DataFrame:
        storedData = pd.read_sql(f'''SELECT * FROM {interval}
                                    WHERE Ticker="{ticker}"''',
                                 con=self.engine,
                                 parse_dates=["Datetime"]).set_index("Datetime").drop(columns=["index"])
        storedData.index = interface.Utils.convertTZ(storedData.index)

        return storedData

    def deleteByTickerInterval(self, ticker: str, interval: str) -> None:
        self.engine.execute(f'''DELETE FROM {interval}
                                WHERE Ticker="{ticker}"''')

    def save(self, newData: pd.DataFrame, ticker: str, interval) -> None:
        newData.columns = [x.replace(' ', '_') for x in newData.columns]
        newData["Ticker"] = ticker

        try:
            storedData = self.findByTickerInterval(ticker, interval)
            newData = pd.concat([storedData.loc[:newData.index[0], :],
                                 newData]).reset_index()
            self.deleteByTickerInterval(ticker, interval)
        except (pymysql.err.ProgrammingError, sqlalchemy.exc.ProgrammingError, KeyError):
            pass

        newData.to_sql(name=interval, con=self.engine, if_exists='append', index=True)
