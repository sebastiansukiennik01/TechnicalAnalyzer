import datetime
import os.path
import unittest

import pandas as pd

import cache.Yahoo as Yahoo


class TestCache(unittest.TestCase):

    def test_init_assign_single_ticker(self):
        ticker = "EURUSD=X"
        y = Yahoo(ticker)
        self.assertEqual(ticker, y.ticker)

    def test_init_assign_multiple_ticker(self):
        ticker = "EURUSD=X GBPUSD=X USDJPY=X"
        y = Yahoo(ticker)
        self.assertEqual(ticker, y.ticker)

    def test_init_assign_interval(self):
        interval = "1h"
        y = Yahoo("EURUSD=X", interval)
        self.assertEqual(interval, y.interval)

    def test_getSP_is_None_on_init(self):
        y = Yahoo("EURUSD=X")
        self.assertIsNone(y.stockPrice)

    def test_getSP_correct_return(self):
        y = Yahoo("EURUSD=X")
        sp = y.getSP()
        self.assertEqual(y.stockPrice, sp)

    def test_downloadData_assigns_stockPrice(self):
        os.chdir('../')
        y = Yahoo("EURUSD=X")
        y.downloadData()
        self.assertTrue(os.path.exists(f"data/forex/{y.interval}/EURUSD=X.csv"))

    def test_loadData_returns_correct(self):
        y = Yahoo("EURUSD=X").loadData("EURUSD=X")
        self.assertIsInstance(y, pd.DataFrame)
        self.assertFalse(y.empty)

    def test_loadData_invalid_ticker(self):
        with self.assertRaises(FileNotFoundError):
            Yahoo(' ').loadData(' ')
        with self.assertRaises(FileNotFoundError):
            Yahoo('EURUSD=X').loadData(' ')

    def test_loadData_interval_applied(self):
        # czy jest zapisany
        y = Yahoo("EURUSD=X")
        y.loadData("EURUSD=X")
        self.assertEqual(y.interval, "5m")

        y.loadData("EURUSD=X", interval="1m")
        self.assertEqual(y.interval, "1m")

        y.loadData("EURUSD=X", interval="2m")
        self.assertEqual(y.interval, "2m")

        y.loadData("EURUSD=X", interval="15m")
        self.assertEqual(y.interval, "15m")

        y.loadData("EURUSD=X", interval="30m")
        self.assertEqual(y.interval, "30m")

        y.loadData("EURUSD=X", interval="60m")
        self.assertEqual(y.interval, "60m")

        y.loadData("EURUSD=X", interval="1h")
        self.assertEqual(y.interval, "1h")

        y.loadData("EURUSD=X", interval="1d")
        self.assertEqual(y.interval, "1d")


if __name__ == '__main__':
    unittest.main()
