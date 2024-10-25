import os
import pandas as pd

from stock_data import download_tickers, get_tickers
from stock_analysis import find_good_stocks

if __name__ == "__main__":
    # End date is now
    end_date = pd.to_datetime("today")

    # Start date is 5 years ago
    start_date = end_date - pd.DateOffset(years=5)

    startDate = pd.to_datetime(start_date)
    endDate = pd.to_datetime(end_date)

    interval = "1d"

    if os.path.exists("stock_tickers.csv"):
        print("File exists")
    else:
        download_tickers()

    tickers = get_tickers()
    print(f"Tickers: {len(tickers)}")

    max_stocks = None

    print("Finding Good Stocks...")
    find_good_stocks(startDate, endDate, interval, tickers, max_stocks)
