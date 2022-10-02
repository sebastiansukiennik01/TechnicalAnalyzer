from cache import Yahoo
from stockPrice import Indicators

import matplotlib.pyplot as plt

if __name__ == '__main__':
    tickers = ["EURUSD=X", "GBPUSD=X", "AUDUSD=X",
               "USDJPY=X", "USDCHF=X", "USDCAD=X"]

    # load data
    forex = Yahoo(tickers)
    eur = forex.loadData(tickers[0], startDate="W-0", endDate="W-0", interval='15m')

    # Add indicators
    eurStock = Indicators(eur).addSMA('Close', length=5)\
        .addEMA()\
        .addRSI()\
        .addMACD()\

    eurStock = eurStock.getSP()

    print(eurStock.tail(20))

    plt.plot(eurStock.loc[:, ['Close_MACD_12_26', 'Close_MACD_sign_12_26']])
    plt.show()


