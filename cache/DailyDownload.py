"""
Script called every day to download and append new data to existing files
"""
import os
# set directory to TechnicalAnalyzer
path_parent = os.path.dirname(os.getcwd())
os.chdir(path_parent)

from Yahoo import Yahoo

FOREX = ["EURUSD=X", "GBPUSD=X", "AUDUSD=X", "USDJPY=X", "USDCHF=X", "USDCAD=X"]
INTERVALS = ["5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]

if __name__ == '__main__':

    for i in INTERVALS:
        y = Yahoo(FOREX, i)
        y.downloadData()
