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

        fig, axs = plt.subplots(1, 1, layout=None)
        axs.plot(x, self.data[y])
        mask = self.data.index[self.data['Buy']]
        axs.vlines(x=mask, ymin=0.97, ymax=1.01, alpha=0.5, colors='green')
        plt.show()


    def addEntries(self, entries: pd.Series, exits: pd.Series):
        pass

