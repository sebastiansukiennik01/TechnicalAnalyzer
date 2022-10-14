from cache import Yahoo
from stockPrice import Indicators, Backtesting
from visualization import LineChart

import matplotlib.pyplot as plt

if __name__ == '__main__':
    tickers = ["EURUSD=X", "GBPUSD=X", "AUDUSD=X",
               "USDJPY=X", "USDCHF=X", "USDCAD=X"]

    # load data
    forex = Yahoo(tickers)
    eur = forex.loadData(tickers[5], interval='5m', startDate='W-2', endDate='W-0')

    # Add indicators
    eurStock = Indicators(eur).addSMA('Close', length=20).addSMA('Close', length=100).addRSI().addMACD()
    eurStock = eurStock.getSP()
    print(eurStock.columns)

    # backtesting
    criteria = Backtesting.Utils.loadCriteria("newHighAfterReversal")
    newHigh = Backtesting.Strategy(eurStock, criteria).executeTrades()

    ent = [t.entryDate for t in newHigh]
    exi = [t.exitDate for t in newHigh]
    [print(f"entry: {t.entryDate}, exit: {t.exitDate} ====> {t.profit}") for t in newHigh]
    print(sum([t.profit for t in newHigh]))

    # graph results
    lc = LineChart(eurStock)
    lc.draw(y=["Close", "Close_sma_20", "Close_sma_100"], entries=ent, exits=exi)



