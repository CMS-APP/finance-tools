import os
import pandas as pd
import sys

from stock_data import download_tickers, get_tickers
from stock_analysis import find_good_stocks
from stock_file import write_good_stock_to_csv
from stock_plotting import plot_stocks
from send_email import default_email_service, email_html

import matplotlib.pyplot as plt

if __name__ == "__main__":
    logging = False
    if len(sys.argv) > 1:
        if (sys.argv[1] == "-l"):
            logging = True

    # End date is now
    end_date = pd.to_datetime("today")

    # Start date is 5 years ago
    start_date = end_date - pd.DateOffset(years=5)

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    interval = "1d"

    # Get the current file directory 
    
    folder_path = os.path.dirname(os.path.realpath(__file__))
    file_name = "all_tickers.csv"
    file_path = os.path.join(folder_path, file_name)

    if os.path.exists(file_path):
        print("File exists")
    else:
        download_tickers()

    tickers = get_tickers()
    print(f"Tickers: {len(tickers)}")
    max_stocks = None
    
    print("Finding Good Stocks...")
    good_stocks = find_good_stocks(start_date, end_date, interval, tickers, max_stocks, logging)
    write_good_stock_to_csv(good_stocks)
    # plot_stocks(good_stocks)

    html = email_html(good_stocks)
    default_email_service(html)

    # plt.show()
