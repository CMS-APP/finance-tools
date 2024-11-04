import pandas as pd
import matplotlib.pyplot as plt
from stock_data import StockData
import time
import sys
import math


def calculate_dow_from_all_time_high():
    """
    Function to calculate how far the Dow Jones is from its all time high
    """

    end_date = pd.to_datetime("today")
    end_date = end_date.strftime("%Y-%m-%d")
    dow = StockData(
        ticker="^DJI", start_date="1928-01-03", end_date=end_date, interval="1d"
    )
    dow.calculate_off_all_time_high()

    print("Dow: Off All Time High:", round(dow.off_all_time_high, 1))

    return dow.off_all_time_high


def calculate_nasdaq_from_all_time_high():
    """
    Function to calculate how far the NASDAQ is from its all time high
    """

    end_date = pd.to_datetime("today")
    end_date = end_date.strftime("%Y-%m-%d")

    nasdaq = StockData(
        ticker="^IXIC", start_date="1971-02-05", end_date=end_date, interval="1d"
    )
    nasdaq.calculate_off_all_time_high()

    print("NASDAQ: Off All Time High:", round(nasdaq.off_all_time_high, 1))

    return nasdaq.off_all_time_high


def find_good_stocks(start_date, end_date, interval, tickers, max_stocks):
    """
    Function to find stocks from tickers list that meet specific criteria.
    """

    dateDelta = end_date - start_date
    if dateDelta.days < 1095:
        print("ERROR: Start and end dates must be at least 1095 days apart.")
        return

    good_stocks = []

    print("Calculating Dow and NASDAQ from all time high...")

    compare_stock_off_all_time_high = calculate_nasdaq_from_all_time_high()
    compare_stock_off_all_time_high = calculate_dow_from_all_time_high()

    start_time = time.time()  # Start time for progress tracking

    for index, ticker in enumerate(tickers):
        try:
            elapsed_time = time.time() - start_time
            avg_time_per_iteration = elapsed_time / (index + 1)
            remaining_time = avg_time_per_iteration * (len(tickers) - index - 1)
            progress = (index + 1) / len(tickers) * 100

            if index > 0:
                sys.stdout.write("\033[F\033[K" * 3)
                sys.stdout.flush()

            done_text = math.floor(progress / 2.5)
            not_done_text = 40 - done_text

            prog_percentage = f"{progress:.2f}"
            prog_text = "Progress: " + f"{prog_percentage}%".ljust(7)

            print(
                "\nTicker:   " + ticker.ljust(7),
                "| Good Tickers: " + str(len(good_stocks)),
                "| Filtered Tickers: " + str(index + 1),
                "| Total Tickers: " + str(len(tickers)),
            )

            print(
                f"{prog_text} | [{'*' * done_text}{' ' * not_done_text}] | Time Remaining: {remaining_time:.2f} seconds"
            )

            company_stock = StockData(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
                interval=interval,
            )
            close = company_stock.data_close

            if (
                close is None
                or not company_stock.year_count
                or company_stock.year_count < 200
                or company_stock.year_count * 5 > len(close)
            ):
                continue

            company_stock.calculate_off_all_time_high()

            # If the stock is more than 10% off its all time high, skip it

            if company_stock.off_all_time_high < -10 + compare_stock_off_all_time_high:
                continue

            company_stock.calculate_ytd_return()

            if company_stock.ytd_return < 30:
                continue

            company_stock.calculate_yearly_return()

            if not all([value > 20 for value in company_stock.yearly_return]):
                continue

            company_stock.calculate_5yr_return()

            if company_stock.five_yr_return < 200:
                continue

            company_stock.calculate_sharpe_ratio()
            company_stock.calculate_stock_volatility()
            good_stocks.append(company_stock)

            if max_stocks is not None and len(good_stocks) == max_stocks:
                return good_stocks

        except Exception as e:
            print(f"Error: {ticker, index} {e}")
            quit()

    return good_stocks
