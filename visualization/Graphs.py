"""
Contains classes and methods used for data visualization. Charting stock price data,
return from strategies, entries and exits of strategies etc.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class LineChart:

    def __init__(self, data: pd.DataFrame, width: int = 12, height: int = 6):
        self.data = data
        self.width = width
        self.height = height

    def draw(self, **kwargs):

        x = kwargs.pop('x', self.data.index)
        y = kwargs.pop('y', self.data.columns[0])
        entries = kwargs.pop('entries')
        exits = kwargs.pop('exits')

        fig, axs = plt.subplots(3, 1, layout=None)
        axs[0].plot(x, self.data[y])
        axs[2].plot(x, self.data['Close_rsi'])
        axs[1].plot(x, np.repeat(0, len(x)), color="black")
        axs[1].plot(x, self.data[['Close_MACD_12_26', 'Close_MACD_sign_12_26']])

        minn = min(self.data["Low"])
        maxx = max(self.data["High"])
        axs[0].vlines(x=entries, ymin=minn, ymax=maxx, alpha=0.5, colors='green')
        axs[0].vlines(x=exits, ymin=minn, ymax=maxx, alpha=0.5, colors='red')
        plt.show()

    def addEntries(self, entries: pd.Series, exits: pd.Series):
        pass

