import yfinance as yf
import numpy as np
import pandas as pd
import os
import math
import logging

logging.getLogger("yfinance").setLevel(logging.CRITICAL)


class StockData:
    # Class which holds data for a specific stock
    def __init__(self, ticker, start_date, end_date, interval):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.interval = interval

        self.data = []
        self.data_close = []

        self.year_count = None
        self.off_all_time_high = None
        self.ytd_return = None
        self.three_yr_return = None
        self.five_yr_return = None
        self.yearly_return = None

        self.sharpe_ratio = None
        self.volatility = None

        try:
            # Download data from yfinance
            data = yf.download(
                tickers=self.ticker,
                interval=interval,
                auto_adjust=True,
                start=start_date,
                end=end_date,
                progress=False,
            )

            # Check if data is empty and handle accordingly
            if not data.empty:
                self.data = data
                info = yf.Ticker(ticker).info
                self.market_cap = info.get('marketCap')
                self.data_close = data["Close"].values.ravel().tolist()
                self.max_close = max(self.data_close)
                self.year_count = math.floor(len(self.data_close) / 5)

        except Exception as e:
            print(f"Error: {e}")

    def calculate_off_all_time_high(self):
        latest_close = self.data_close[-1]
        self.off_all_time_high = ((latest_close / self.max_close) - 1) * 100

    def calculate_ytd_return(self):
        latest_close = self.data_close[-1]
        yr_close = self.data_close[-self.year_count]
        self.ytd_return = ((latest_close / yr_close) - 1) * 100

    def calculate_5yr_return(self):
        latest_close = self.data_close[-1]
        five_yr_close = self.data_close[-self.year_count * 5]
        self.five_yr_return = ((latest_close / five_yr_close) - 1) * 100

    def calculate_yearly_return(self):
        yearly_return = []
        for i in range(3):
            pre_yr_close = self.data_close[-self.year_count * (i + 1) - 1]
            post_yr_close = self.data_close[-self.year_count * i - 1]
            year_return = ((post_yr_close / pre_yr_close) - 1) * 100

            yearly_return.append(year_return)
        self.yearly_return = yearly_return

    def calculate_sharpe_ratio(self):
        # Calculates the sharpe ratio for the stock
        risk_free_rate = 0.05 / 252
        pct_changes = [
            (self.data_close[i] - self.data_close[i - 1]) / self.data_close[i - 1]
            for i in range(1, len(self.data_close))
        ]
        sharpe_ratio = (np.mean(pct_changes) - risk_free_rate) / np.std(pct_changes)
        self.sharpe_ratio = sharpe_ratio * np.sqrt(len(pct_changes))

    def calculate_stock_volatility(self):
        # Calculates the volatility of the stock
        returns = np.diff(self.data_close) / self.data_close[:-1]
        self.volatility = np.std(returns) * np.sqrt(len(returns))


def download_tickers():
    print("Getting Tickers")
    url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt"

    # Download the file and load it into a DataFrame
    df = pd.read_csv(url, sep="|")

    # Get the current working directory
    folder_path = os.path.dirname(os.path.realpath(__file__))
    file_name = "all_tickers.csv"
    file_path = os.path.join(folder_path, file_name)

    # Save DataFrame to a local CSV file
    df.to_csv(
        file_path, index=False
    )  # Set index=False to avoid saving the index column

    print("Tickers saved to stock_tickers.csv")
    print("Got Tickers")


def get_tickers(stock_type="all"):
    tickers = []

    folder_path = os.path.dirname(os.path.realpath(__file__))
    file_name = "all_tickers.csv"
    
    if stock_type == "all":
        file_name = "all_tickers.csv"
    elif stock_type == "us":
        file_name = "stock_tickers.csv"

    file_path = os.path.join(folder_path, file_name)

    f = open(file_path, "r", encoding="cp1252")
    for line in f.readlines()[1:]:
        tickers.append(line.split(",")[0].replace("\n", ""))
    f.close()

    return tickers  # Return a list of tickers
