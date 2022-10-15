from cache import Yahoo
from stockPrice import Indicators, Backtesting, StockPrice
from visualization import LineChart
import cache
import dataBase

import matplotlib.pyplot as plt

if __name__ == '__main__':
    tickers = ["EURUSD=X", "GBPUSD=X", "AUDUSD=X",
               "USDJPY=X", "USDCHF=X", "USDCAD=X"]

    # load data

    cache.run()


    breakpoint()
    data = dataBase.StockPriceDb().findByTicker("EURUSD=X", "5m")
    data = StockPrice(data).applyDateRange("W-3", "W-0")
    # Add indicators
    eurStock = Indicators(data).addSMA('Close', length=20)\
        .addSMA('Close', length=150)\
        .addRSI()\
        .addMACD()
    eurStock = eurStock.getSP()
    print(eurStock.columns)

    # backtesting
    criteria = Backtesting.StrategyUtils.loadCriteria("newHighAfterReversal")
    newHigh = Backtesting.Strategy(eurStock, criteria).executeTrades()

    ent = [t.entryDate for t in newHigh]
    exi = [t.exitDate for t in newHigh]
    [print(f"entry: {t.entryDate}, exit: {t.exitDate} ====> {t.profit}") for t in newHigh]
    print(sum([t.profit for t in newHigh]))

    # graph results
    lc = LineChart(eurStock)
    lc.draw(y=["Close", "Close_sma_20", "Close_sma_150"], entries=ent, exits=exi)



