"""
Script called every day to download and append new data to existing files
"""


import os

os.chdir("/Users/admin/Desktop/TechnicalAnalyzer/TechnicalAnalyzer/")

import cache
import dataBase

FOREX = ["EURUSD=X", "GBPUSD=X", "AUDUSD=X", "USDJPY=X", "USDCHF=X", "USDCAD=X"]
INTERVALS = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]

def run():
    for inter in INTERVALS:
        y = cache.Yahoo(FOREX, inter)
        y.downloadData()
        db = dataBase.StockPriceDb()
        for f in FOREX:
            tickData = y.loadData(f)
            db.save(tickData, f, inter)


if __name__ == '__main__':
    run()

