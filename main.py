from cache import Yahoo

if __name__ == '__main__':
    tickers = ["EURUSD=X", "GBPUSD=X"]

    forex = Yahoo(tickers)
    forex.getData()
