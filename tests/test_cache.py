import os.path
import unittest
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


if __name__ == '__main__':
    unittest.main()
