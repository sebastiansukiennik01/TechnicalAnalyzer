from cache import Yahoo
from stockPrice import Indicators, Backtesting
from visualization import LineChart

import matplotlib.pyplot as plt

if __name__ == '__main__':
    tickers = ["EURUSD=X", "GBPUSD=X", "AUDUSD=X",
               "USDJPY=X", "USDCHF=X", "USDCAD=X"]

    # load data
    forex = Yahoo(tickers)
    eur = forex.loadData(tickers[0], interval='5m', startDate='W-0', endDate='W-0')

    # Add indicators
    eurStock = Indicators(eur).addSMA('Close', length=20)
    eurStock = eurStock.getSP()

    # backtesting
    criteria = Backtesting.Utils.loadCriteria("newHighAfterReversal")
    newHigh = Backtesting.Strategy(eurStock, criteria).run()
    print(newHigh.getSP().head())

    # graph results
    lc = LineChart(newHigh.getSP())
    lc.draw(y=['Close', 'Close_sma_20'])

