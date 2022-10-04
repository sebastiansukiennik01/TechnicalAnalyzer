from cache import Yahoo
from stockPrice import Indicators, Backtesting

import matplotlib.pyplot as plt

if __name__ == '__main__':
    tickers = ["EURUSD=X", "GBPUSD=X", "AUDUSD=X",
               "USDJPY=X", "USDCHF=X", "USDCAD=X"]

    # load data
    forex = Yahoo(tickers, interval='1m')
    forex.downloadData()
    eur = forex.loadData(tickers[0], startDate="W-0", endDate="W-0", interval='1m')

    # Add indicators
    eurStock = Indicators(eur).addSMA('Close', length=20).addEMA().addRSI().addMACD()
    eurStock = eurStock.getSP()

    # backtesting
    criteria = Backtesting.Utils.loadCriteria("newHighAfterReversal")
    newHigh = Backtesting.NewHighAfterReversal(eurStock, criteria).run()
    print(newHigh.getSP()[["Buy", "Sell"]])

