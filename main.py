import os
import pandas as pd

from stock_data import download_tickers, get_tickers
from stock_analysis import find_good_stocks
from stock_file import write_good_stock_to_csv
from stock_plotting import plot_stocks

import matplotlib.pyplot as plt

if __name__ == "__main__":
    # End date is now
    end_date = pd.to_datetime("today")

    # Start date is 5 years ago
    start_date = end_date - pd.DateOffset(years=5)

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    interval = "1d"

    if os.path.exists("all_tickers.csv"):
        print("File exists")
    else:
        download_tickers()

    tickers = get_tickers()
    print(f"Tickers: {len(tickers)}")
    max_stocks = None

    print("Finding Good Stocks...")
    good_stocks = find_good_stocks(start_date, end_date, interval, tickers, max_stocks)
    write_good_stock_to_csv(good_stocks)
    plot_stocks(good_stocks)

    plt.show()
