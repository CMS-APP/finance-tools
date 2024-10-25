import pandas as pd
import matplotlib.pyplot as plt
from stock_data import StockData


def find_good_stocks(startDate, endDate, interval, tickers, max_stocks):
    """
    Function to find the stock from tickers list:
    These stocks must have a:
     - 20% yearly return per year
     - 30% yearly return to date
     - 100% return over the last 3 years

    This function also calculates and returns the
    """

    # Check if the number of days between the start and end date is equal to or above 1095 days.
    dateDelta = endDate - startDate
    if dateDelta.days < 1095:
        print(
            "================================================================================"
        )
        print(
            "ERROR\nThe start and end dates are too close together\nCurrently the two dates are {} days apart, however they need to be at least 1095 days apart".format(
                dateDelta.days
            )
        )
        return

    fig, ax = plt.subplots(nrows=3, ncols=3)
    subFigureNumX = 0
    subFigureNumY = 0
    goodStockNum = 0
    returnOnInvestment = {}

    for index, ticker in enumerate(tickers):
        companyStock = StockData(
            ticker=ticker, startDate=startDate, endDate=endDate, interval=interval
        )
        close = companyStock.dataClose

        if close != None and len(close) >= 1095:
            print(
                "Company:",
                ticker,
                "|| Good Companies Found:",
                goodStockNum,
                "|| Total Companies Filtered:",
                index,
            )

            # Redefining important values
            maxH = max(close)
            cH = close[-1]
            yOneH = close[-365]
            yTwoH = close[-730]
            yThreeH = close[-1095]

            if (cH * 1.25) >= maxH:
                print("Close to All Time High - Yes")
            else:
                print("Close to All Time High - No")
                continue

            if maxH >= (yOneH * 1.3):
                print("30% yearly return to date - Yes")
            else:
                print("30% yearly return to date - No")
                continue

            if yOneH >= yTwoH * 1.2 and yTwoH >= yThreeH * 1.2:
                print("20% yearly return per year - Yes")
            else:
                print("20% yearly return per year - No")
                continue

            if maxH >= (yThreeH * 2):
                print("100% return over the last 3 years - Yes")
            else:
                print("100% return over the last 3 years - No")
                continue

            goodStockNum += 1

            # Plotting the data on one of the subgraphs
            ax[subFigureNumY][subFigureNumX].plot(
                range(len(close)), close, color="green", label=ticker
            )
            ax[subFigureNumY][subFigureNumX].legend()
            returnOnInvestment[ticker] = (maxH / close[0]) * 100

            # Altering the plotting location for the next subgraphs
            if subFigureNumX == 2:
                if subFigureNumY == 2:
                    subFigureNumX = 0
                    subFigureNumY = 0

                    fig, ax = plt.subplots(nrows=3, ncols=3)
                else:
                    subFigureNumX = 0
                    subFigureNumY += 1
            else:
                subFigureNumX += 1

        if max_stocks != None and goodStockNum == max_stocks:
            plt.show()
            break

    plt.show()
