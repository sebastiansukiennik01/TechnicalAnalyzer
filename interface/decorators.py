"""
Contains decorators, useful for debugging.
"""
import datetime as dt
import time
import os


def debug(func):
    def _wraper(*args, **kwargs):
        argType = [[type(a), a] for a in args]
        kwargType = [[type(v), k, v] for k, v in kwargs.items()]
        print(f"\n##### {func.__name__} #####\nArgs: {argType}\nKwargs: {kwargType}")
        val = func(*args, **kwargs)
        print(f"Returns: {[type(val), val]}")
        return val

    return _wraper


def timer(func):
    def _timer(*args, **kwargs):
        start = time.perf_counter()
        print(args)
        val = func(*args, **kwargs)
        print(f"\n##### Function {func.__name__} took: {time.perf_counter() - start} s")
        return val

    return _timer


def log(func):
    def _log(*args, **kwargs):
        argType = [[type(a), a.__name__] for a in args]
        kwargType = [[type(v), k, v.__name__] for k, v in kwargs.items()]
        filePath = os.path("data/logs") / "downloadInfo.txt"
        now = dt.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        with open(filePath, 'a') as f:
            f.write(f"{now}: {func.__name__} with args: {argType}, kwargs: {kwargType}")

        return func(*args, **kwargs)

    return _log
