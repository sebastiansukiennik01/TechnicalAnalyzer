"""
Contatins class with tools needed to convert/check/asses types and other general use
function.
"""
import pandas as pd


class Utils(object):
    @staticmethod
    def convertTZ(dates: (list[pd.DatetimeIndex] | list), timeZone: str = "Europe/Warsaw"):
        if not isinstance(dates, pd.DatetimeIndex):
            dates = pd.DatetimeIndex(dates)
        try:
            return dates.tz_convert(timeZone)
        except TypeError:
            return dates.tz_localize(timeZone)

    @staticmethod
    def isFloat(k: (str | float | int)):
        try:
            float(k)
            return True
        except ValueError:
            return False
