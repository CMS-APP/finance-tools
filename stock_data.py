import yfinance as yf
import pandas_datareader as pdr
import pandas as pd


class StockData:
    # Class which holds data for a specific stock
    def __init__(self, ticker, startDate, endDate, interval):
        self.ticker = ticker
        self.startDate = startDate
        self.endDate = endDate
        self.interval = interval

        try :
            # Download data from yfinance
            data = yf.download(
                tickers=self.ticker,
                interval=interval,
                auto_adjust=True,
                start=startDate,
                end=endDate,
            )

            # Check if data is empty and handle accordingly
            if data.empty:
                print(f"No data found for ticker {ticker} in the given date range.")
                self.data = data
                self.dataClose = []
                self.dataOpen = []
                self.dataHigh = []
                self.dataLow = []
            else:
                self.data = data
                self.dataClose = (
                    data["Close"].values.ravel().tolist()
                )  # Convert the 'Close' column to a list
                self.dataOpen = (
                    data["Open"].values.ravel().tolist()
                )  # Convert the 'Open' column to a list
                self.dataHigh = (
                    data["High"].values.ravel().tolist()
                )  # Convert the 'High' column to a list
                self.dataLow = (
                    data["Low"].values.ravel().tolist()
                )  # Convert the 'Low' column to a list
        except Exception as e:
            print(f"Error: {e}")
            self.data = None
            self.dataClose = []
            self.dataOpen = []
            self.dataHigh = []
            self.dataLow = []

def download_tickers():
    print("Getting Tickers")
    # URL used by `pandas_datareader` to fetch NASDAQ symbols
    url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt"

    # Download the file and load it into a DataFrame
    df = pd.read_csv(url, sep="|")

    # Save DataFrame to a local CSV file
    df.to_csv(
        "stock_tickers.csv", index=False
    )  # Set index=False to avoid saving the index column

    print("Tickers saved to stock_tickers.csv")
    print("Got Tickers")


def get_tickers():
    # Read the CSV file and return just a list of tickers
    data = pd.read_csv("stock_tickers.csv")
    return data["Symbol"].tolist()[:-1]  # Return a list of tickers
