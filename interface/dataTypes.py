"""
Contains custom data types. User for type hints in class/function declarations.
"""
import pandas as pd
import datetime as dt

dateType = (str | dt.datetime | pd.Timestamp)

