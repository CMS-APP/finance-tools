import yfinance as yf
import numpy as np
import pandas as pd
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
                self.data_close = data["Close"].values.ravel().tolist()
                self.max_close = max(self.data_close)

                self.year_count = math.floor(len(self.data_close) / 5)

        except Exception as e:
            print(f"Error: {e}")

    def calculate_off_all_time_high(self):
        latest_close = self.data_close[-1]
        self.off_all_time_high = latest_close / self.max_close
        # print("Off All Time High:", round((1 - self.off_all_time_high) * 100, 1))

    def calculate_ytd_return(self):
        self.ytd_return = self.data_close[-1] / self.data_close[-self.year_count]
        # print("Year To Date Return:", self.ytd_return)

    def calculate_5yr_return(self):
        self.five_yr_return = (
            self.data_close[-1] / self.data_close[-self.year_count * 5]
        )
        # print("Five Year Return:", self.five_yr_return)

    def calculate_yearly_return(self):
        yearly_return = []
        for i in range(3):
            year_return = (
                self.data_close[-self.year_count * (i) - 1]
                / self.data_close[-self.year_count * (i + 1) - 1]
            )

            yearly_return.append(round((year_return * 100) - 100, 1))
        self.yearly_return = yearly_return
        # print("Yearly Return:", yearly_return)

    def calculate_sharpe_ratio(self):
        # Calculates the sharpe ratio for the stock
        risk_free_rate = 0.04 / 252
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

    # Save DataFrame to a local CSV file
    df.to_csv(
        "stock_tickers.csv", index=False
    )  # Set index=False to avoid saving the index column

    print("Tickers saved to stock_tickers.csv")
    print("Got Tickers")


def get_tickers(stock_type="all"):
    tickers = []

    if stock_type == "all":
        file_name = "all_tickers.csv"
    elif stock_type == "us":
        file_name = "stock_tickers.csv"

    f = open(file_name, "r", encoding="cp1252")
    for line in f.readlines()[1:]:
        tickers.append(line.split(",")[0].replace("\n", ""))
    f.close()

    return tickers  # Return a list of tickers
