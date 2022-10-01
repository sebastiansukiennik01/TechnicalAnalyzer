from cache import Yahoo
from stockPrice import StockPrice, Indicators

if __name__ == '__main__':
    tickers = ["EURUSD=X", "GBPUSD=X", "AUDUSD=X",
               "USDJPY=X", "USDCHF=X", "USDCAD=X"]

    forex = Yahoo(tickers)
    # forex.getData()
    eur = forex.loadData(tickers[0], startDate="W-0", endDate="W-0", interval='15m')
    print(eur.head())
    Indicators.SMA(eur)

