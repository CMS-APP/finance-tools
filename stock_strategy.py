import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
from stock_data import StockData


def getDateListFromIndexList(startDate, indexList):
    # Function to get a list of dates from a list of indexes
    dateList = []
    for index in indexList:
        dayInt = int(index * (365.25 / 253))
        d = dt.timedelta(days=dayInt)
        a = startDate + d
        dateList.append(a)
    return dateList


def plotStockWithVIX(
    company, name, startDate, endDate, interval, lowerVIXVal, upperVIXVal, plot=True
):
    # Function to pick VIX lower and upper bounds and plot the resulting stock

    # Get VIX and stock data
    vixStock = StockData(
        ticker="^VIX", startDate=startDate, endDate=endDate, interval=interval
    )
    companyStock = StockData(
        ticker=company, startDate=startDate, endDate=endDate, interval=interval
    )

    vixDataAverage = vixStock.dataAverage
    companyDataAverage = companyStock.dataAverage

    # Lists to hold all the data
    indexList = []
    vixDataList = []
    dataList = []

    # Lists to hold the current data for a series of days - to be able to plot with gaps
    newIndexList = []
    newVixDataList = []
    newDataList = []

    # Iterate through the vix and company data and see if the vix value is between the bounds
    for index, (vixData, companyData) in enumerate(
        zip(vixDataAverage, companyDataAverage)
    ):
        # If it is not between the bounds reset the lists
        if vixData < lowerVIXVal or vixData > upperVIXVal:
            if len(newIndexList) > 1:
                indexList.append(newIndexList)
                vixDataList.append(newVixDataList)
                dataList.append(newDataList)

            newIndexList = []
            newVixDataList = []
            newDataList = []
        else:
            newIndexList.append(index)
            newVixDataList.append(vixData)
            newDataList.append(companyData)

    if len(newIndexList) > 1:
        indexList.append(newIndexList)
        vixDataList.append(newVixDataList)
        dataList.append(newDataList)

    if plot:
        fig, ax = plt.subplots(2, 1, figsize=(10, 7))

        legend = False
        for index, vixData, companyData in zip(indexList, vixDataList, dataList):
            dateList = getDateListFromIndexList(startDate, index)
            if legend == False:
                ax[0].plot(dateList[0], companyData[0], "go")
                ax[0].plot(dateList, companyData, "b", label=name)
                ax[0].plot(
                    dateList[len(companyData) - 1],
                    companyData[len(companyData) - 1],
                    "ro",
                )
                ax[1].plot(dateList, vixData, "r", label="VIX")
                legend = True
            else:
                ax[0].plot(dateList, companyData, "b")
                ax[1].plot(dateList, vixData, "r")
                ax[0].plot(dateList[0], companyData[0], "go")
                ax[0].plot(
                    dateList[len(companyData) - 1],
                    companyData[len(companyData) - 1],
                    "ro",
                )

        ax[0].tick_params(axis="x", rotation=60)
        ax[0].set_ylabel("Stock Price ($)")
        ax[1].tick_params(axis="x", rotation=60)
        ax[1].set_ylabel("VIX Price ($)")
        ax[0].set_title(
            "Plotting VIX with {} - for a VIX Range of: {} - {}".format(
                name, lowerVIXVal, upperVIXVal
            )
        )

    return dataList


def stockDataFromVIX(company, name, startDate, endDate, interval):
    # Function to calculate a few statistic for each VIX value, these include:
    # Variance, range, and trend.

    def updateDict(dataDict, vixValue, newValue):
        # Function used to update the specific dictionary
        newList = dataDict[vixValue]
        newList.append(newValue)
        dataDict[vixValue] = newList
        return dataDict

    def calculateRange(dataDict, vixValue, dataList):
        # Calculate the difference between the max and min value in the list
        newValue = max(dataList) - min(dataList)
        return updateDict(dataDict, vixValue, newValue)

    def calculateTrend(dataDict, vixValue, dataList):
        # Calculate the difference between the first and last value in the list
        newValue = dataList[len(dataList) - 1] - dataList[0]
        return updateDict(dataDict, vixValue, newValue)

    def calculateVariance(dataDict, vixValue, dataList):
        mean = sum(dataList) / len(dataList)
        topPart = sum([(dataVal - mean) ** 2 for dataVal in dataList])
        variance = topPart / (len(dataList) - 1)
        return updateDict(dataDict, vixValue, variance)

    def plotAllData(indexList, dataList, ax, title):
        # Add data and line of best fit to plot
        ax.plot(indexList, dataList, "r")
        a, b = np.polyfit(list(indexList), list(dataList), 1)
        ax.plot(indexList, a * np.array(list(indexList)) + b, "b")
        ax.set_xlabel("VIX Value ($)")
        ax.set_title(title)

    # Get VIX and stock data
    vixStock = StockData(
        ticker="^VIX", startDate=startDate, endDate=endDate, interval=interval
    )
    companyStock = StockData(
        ticker=company, startDate=startDate, endDate=endDate, interval=interval
    )

    # Record VIX data in different dictionaries
    vixVarianceDict = {}
    vixTrendDict = {}
    vixRangeDict = {}
    for i in range(1, 100):
        vixVarianceDict[i] = []
        vixTrendDict[i] = []
        vixRangeDict[i] = []

    vixDataAverage = vixStock.dataAverage
    companyDataAverage = companyStock.dataAverage

    # Iterate through each VIX value
    for vixKey in list(vixVarianceDict.keys()):
        dataSeries = []
        # Iterate through each stock price and check if it is in the VIX range
        for index, companyData in enumerate(companyDataAverage):
            if (
                vixDataAverage[index] > vixKey + 0.5
                or vixDataAverage[index] < vixKey - 0.5
            ):
                if len(dataSeries) > 1:
                    vixVarianceDict = calculateRange(
                        vixVarianceDict, vixKey, dataSeries
                    )
                    vixTrendDict = calculateTrend(vixTrendDict, vixKey, dataSeries)
                    vixRangeDict = calculateVariance(vixRangeDict, vixKey, dataSeries)
                dataSeries = []
            dataSeries.append(companyData)

        if len(dataSeries) > 1:
            vixVarianceDict = calculateRange(vixVarianceDict, vixKey, dataSeries)
            vixTrendDict = calculateTrend(vixTrendDict, vixKey, dataSeries)
            vixRangeDict = calculateVariance(vixRangeDict, vixKey, dataSeries)

    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(12, 6))

    # Redefine new dictionaries to remove zero values from the plots
    newVixVarianceDict = {}
    newVixTrendDict = {}
    newVixRangeDict = {}
    for vixKey, vixVarianceValues, vixTrendValues, vixRangeValues in zip(
        vixVarianceDict.keys(),
        vixVarianceDict.values(),
        vixTrendDict.values(),
        vixRangeDict.values(),
    ):
        if len(vixVarianceValues) > 0:
            newVixVarianceDict[vixKey] = sum(vixVarianceDict[vixKey]) / len(
                vixVarianceDict[vixKey]
            )
            newVixTrendDict[vixKey] = sum(vixTrendDict[vixKey]) / len(
                vixTrendDict[vixKey]
            )
            newVixRangeDict[vixKey] = sum(vixRangeDict[vixKey]) / len(
                vixRangeDict[vixKey]
            )

    # Plot all data
    plotAllData(
        newVixVarianceDict.keys(), newVixVarianceDict.values(), ax[0], "Variance"
    )
    plotAllData(newVixTrendDict.keys(), newVixTrendDict.values(), ax[1], "Trend")
    plotAllData(newVixRangeDict.keys(), newVixRangeDict.values(), ax[2], "Range")

    # Save graph to desktop
    fig.suptitle("VIX Specific Data For: {}".format(name), fontsize=20)
    plt.savefig("Graphs/VIXSpecificData/{}.png".format(name))


def findVIXValForHighs(company, name, startDate, endDate, interval):
    # Find VIX values for all time highs for a specific stock

    # Grab VIX and stock data
    vixStock = StockData(
        ticker="^VIX", startDate=startDate, endDate=endDate, interval=interval
    )
    companyStock = StockData(
        ticker=company, startDate=startDate, endDate=endDate, interval=interval
    )

    companyDataAverage = companyStock.dataAverage
    vixDataAverage = vixStock.dataAverage

    prevAllTimeHigh = companyDataAverage[0]
    newHighIndexes = []
    newHighValues = []
    vixHighValues = []

    # Record VIX data
    vixDict = {}
    for i in range(1, 100):
        vixDict[i] = 0

    # Goes through each value and sees if an all time high has been reached
    for index, averageVal in enumerate(companyDataAverage[1:]):
        if averageVal > prevAllTimeHigh and index < len(vixDataAverage):
            prevAllTimeHigh = averageVal

            newHighIndexes.append(index)
            # Record the all time high value as well as the VIX values
            newHighValues.append(averageVal)
            vixHighValues.append(vixDataAverage[index])

            roundedVIXInteger = int(round(vixDataAverage[index]))
            newValue = vixDict[roundedVIXInteger] + 1
            vixDict[roundedVIXInteger] = newValue

    # Create matplotlib figure
    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(12, 6))
    fig.suptitle("All Time High Data for: {}".format(name), fontsize=20)

    # Print the exact number to the user
    for key, value in zip(list(vixDict.keys()), list(vixDict.values())):
        if value != 0:
            print("VIX value:", key, " -- Number of all time highs:", value)

    print("Total number of all time highs:", sum(list(vixDict.values())))

    dateList = getDateListFromIndexList(startDate, newHighIndexes)

    ax[0].plot(dateList, newHighValues, "b")
    ax[0].tick_params(axis="x", rotation=60)
    ax[0].set_title("All Time High Prices", fontsize=10)

    indexList = []
    dataList = []

    for absIndex, (index, value) in enumerate(zip(newHighIndexes, vixHighValues)):
        indexList.append(index)
        dataList.append(value)

        if (
            absIndex < len(newHighIndexes) - 1
            and newHighIndexes[absIndex] + 1 != newHighIndexes[absIndex + 1]
        ):
            dateList = getDateListFromIndexList(startDate, indexList)
            ax[1].scatter(dateList, dataList, c="r")
            indexList = []
            dataList = []

    if len(indexList) != 0:
        dateList = getDateListFromIndexList(startDate, indexList)
        ax[1].scatter(indexList, dataList, c="r")

    ax[1].set_title("VIX Value at New All Times Highs", fontsize=10)
    ax[1].tick_params(axis="x", rotation=60)

    ax[2].plot(list(vixDict.keys()), list(vixDict.values()), "g")
    ax[2].set_title("Number of All Time Highs for Each VIX Value", fontsize=10)

    plt.savefig("Graphs/AllTimeHighData/{}.png".format(name))


def calcPosNegFromVIX(company, name, startDate, endDate, interval):
    # Function to sperate the number of positive vs negative days for different VIX values for a specific stock

    # Get VIX and company data
    vixStock = StockData(
        ticker="^VIX", startDate=startDate, endDate=endDate, interval=interval
    )
    companyStock = StockData(
        ticker=company, startDate=startDate, endDate=endDate, interval=interval
    )

    companyDataOpen = companyStock.dataOpen
    companyDataClose = companyStock.dataClose
    vixDataAverage = vixStock.dataAverage

    # Create dictionary with data inside
    vixPositiveDict = {}
    vixNegativeDict = {}
    for i in range(1, 100):
        vixPositiveDict[i] = 0
        vixNegativeDict[i] = 0

    # Finding the open and close for each day
    for openData, closeData, vixData in zip(
        companyDataOpen, companyDataClose, vixDataAverage
    ):
        vixValue = int(round(vixData))
        # If it is a positive day add to the positive dictionary
        if openData <= closeData:
            currentValues = vixPositiveDict[vixValue]
            currentValues += 1
            vixPositiveDict[vixValue] = currentValues
        # If it is a negative day add to the negative dictionary
        elif openData > closeData:
            currentValues = vixNegativeDict[vixValue]
            currentValues += 1
            vixNegativeDict[vixValue] = currentValues

    # Printing values to user
    for vixValue, vixPositiveNum, vixNegativeNum in zip(
        list(vixPositiveDict.keys()),
        list(vixPositiveDict.values()),
        list(vixNegativeDict.values()),
    ):
        print(
            vixValue,
            vixPositiveNum,
            (vixPositiveNum / sum(list(vixPositiveDict.values()))) * 100,
            "---",
            vixNegativeNum,
            (vixNegativeNum / sum(list(vixNegativeDict.values()))) * 100,
        )

    plt.figure(figsize=(10, 6))
    plt.plot(
        list(vixPositiveDict.keys()),
        list(vixPositiveDict.values()),
        "g",
        label="Positive Days",
    )
    plt.plot(
        list(vixNegativeDict.keys()),
        list(vixNegativeDict.values()),
        "r",
        label="Negative Days",
    )
    plt.title(
        "The Percentage Off the All Time High for Different VIX values for: {}".format(
            name
        )
    )
    plt.xlabel("VIX Value ($)")
    plt.ylabel("Total days")
    plt.legend()
    plt.savefig("Graphs/PosNegFromVIX/{}.png".format(name))


def calcPercentageOffAlltime(company, name, startDate, endDate, interval):
    # Function to calculate the percentage off the all time high for each VIX level for a specific stock.

    # Grabbing the data for the VIX and the specific stock.
    vixStock = StockData(
        ticker="^VIX", startDate=startDate, endDate=endDate, interval=interval
    )
    companyStock = StockData(
        ticker=company, startDate=startDate, endDate=endDate, interval=interval
    )

    companyDataAverage = companyStock.dataAverage
    vixDataAverage = vixStock.dataAverage

    # Creating dictionary holding the data for the percentage off all time high
    vixDict = {}
    for i in range(1, 100):
        vixDict[i] = []

    # Going through each data point except the first
    for index, (vixData, averageData) in enumerate(
        zip(vixDataAverage[1:], companyDataAverage[1:])
    ):
        # Calculaing the all time high up to that point
        allTimeHigh = max(companyDataAverage[0 : index + 1])
        # Calculate the percentage difference from the all time high
        percentageDiff = ((-allTimeHigh + averageData) * 100) / allTimeHigh
        vixValue = int(round(vixData))

        # Save the value for the specific VIX value
        currentList = vixDict[vixValue]
        currentList.append(percentageDiff)
        vixDict[vixValue] = currentList

    # Find the mean percentage difference for each VIX value
    for index, values in zip(list(vixDict.keys()), list(vixDict.values())):
        if len(values) > 0:
            valuesMean = sum(values) / len(values)
            vixDict[index] = valuesMean
        else:
            vixDict[index] = 0

    plt.figure(figsize=(10, 6))
    plt.plot(list(vixDict.keys()), list(vixDict.values()), "b")
    plt.title(
        "The Percentage Off the All Time High for Different VIX values for: {}".format(
            name
        )
    )
    plt.xlabel("VIX Value ($)")
    plt.ylabel("Percentage Difference (%)")
    plt.savefig("Graphs/AllTimeHighDiff/{}.png".format(name))


def mainFunc():
    startDate = dt.datetime(2022, 1, 1)
    endDate = dt.datetime.now()

    indexTickers = {
        "NASDAQ": "^IXIC",
        "DAX": "^GDAXI",
        "SP500": "^GSPC",
        "DOW": "^DJI",
        "FTSE100": "^FTSE",
        "Nikkei": "^N225",
        "HANG": "^HSI",
        "NIFTY50": "^NSEI",
        "FANG": "FNGU",
    }

    companyTickers = {
        "Apple": "AAPL",
        "Google": "GOOG",
        "Netflix": "NFLX",
        "Amazon": "AMZN",
        "Tesla": "TSLA",
        "Meta": "META",
        "Peloton": "PTON",
        "SquareSpace": "SPCE",
        "Twitter": "TWTR",
        "Novo": "NVO",
    }

    interval = "1d"
    name = "Amazon"
    # company = indexTickers[name]
    company = companyTickers[name]

    sell = False

    vixValues = list(range(20, 100))
    portfolioValues = []

    for i in vixValues:
        lowerVIXVal = 0
        upperVIXVal = i / 2

        dataList = plotStockWithVIX(
            company, name, startDate, endDate, interval, lowerVIXVal, upperVIXVal, False
        )

        portfolioValue = float(10000)

        for valueList in dataList:
            startPrice = valueList[0]
            endPrice = valueList[len(valueList) - 1]
            ratio = portfolioValue / startPrice

            if sell:
                profit = -ratio * (endPrice - startPrice)
            else:
                profit = ratio * (endPrice - startPrice)

            portfolioValue += profit
        portfolioValues.append(portfolioValue)

    plt.plot([value / 2 for value in vixValues], portfolioValues)
    plt.show()


def AverageVixvalue():
    startDate = dt.datetime(2000, 1, 1)
    endDate = dt.datetime.now()
    interval = "1d"

    vixStock = StockData(
        ticker="^VIX", startDate=startDate, endDate=endDate, interval=interval
    )
    vixValues = vixStock.dataAverage

    x = [i for i in range(len(vixValues))]
    averageVixValue = sum(vixValues) / len(x)
    print(averageVixValue)
    maxVixValue = max(vixValues)
    minVixValue = min(vixValues)
    print(maxVixValue, minVixValue)

    trendIndexes = []
    trendValues = []
    trendLengths = []

    fig, axs = plt.subplots(1, 2, tight_layout=True)

    downwardTrend = False

    for index, value in enumerate(vixValues):
        if value < 18 or (downwardTrend and value < 20):
            trendIndexes.append(index)
            trendValues.append(value)
            downwardTrend = True
        elif downwardTrend and value > 20:
            downwardTrend = False
            if len(trendValues) >= 2:
                axs[0].plot(trendIndexes, trendValues, "g")
                trendLengths.append(len(trendIndexes))

            trendIndexes = []
            trendValues = []

    axs[1].hist(trendLengths, bins=20)
    plt.show()


if __name__ == "__main__":
    AverageVixvalue()
