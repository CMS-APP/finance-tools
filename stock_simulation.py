import datetime as dt
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import uuid


class StockData:
    def __init__(self, ticker, startDate, endDate, interval):
        self.ticker = ticker

        try:
            data = yf.download(
                tickers=ticker,
                interval=interval,
                auto_adjust=True,
                start=startDate,
                end=endDate,
            )
            self.dataClose = data["Close"].tolist()
            self.dataHigh = data["High"].tolist()
            self.dataLow = data["Low"].tolist()
            self.dataOpen = data["Open"].tolist()

        except:
            raise ValueError("No data found for ticker {} in the given date range.".format(ticker))


class Stock:
    def __init__(self, name, price, volume, stockType):
        self.uniqueId = uuid.uuid1()
        self.name = name
        self.price = price
        self.volume = volume
        self.stockType = stockType

    def notionalValue(self):
        print(self.volume * self.price)


class FinancialSimulation:
    def __init__(self, startingCash):
        self.startingCash = startingCash
        self.cash = startingCash

        self.boughtStocks = []
        self.soldStocks = []

    def buyStock(self, name, buyPrice, volume):
        # Remove stock price from cash
        totalStockValue = buyPrice * volume

        # If there is enough money in the account
        if self.cash - totalStockValue > 0:
            self.cash -= totalStockValue

            newStock = Stock(name, buyPrice, volume, "Buy")
            self.boughtStocks.append(newStock)
            return newStock.uniqueId

    def sellBoughtStock(self, uniqueId, sellPrice):
        for index, stock in enumerate(self.boughtStocks):
            if stock.uniqueId == uniqueId:
                newTotalStockValue = sellPrice * stock.volume
                self.cash += newTotalStockValue
                self.boughtStocks.pop(index)
                return

    def sellStock(self, name, sellPrice, volume):
        # Remove stock price from cash
        totalStockValue = sellPrice * volume

        # If there is enough money in the account
        if self.cash - totalStockValue > 0:
            newStock = Stock(name, sellPrice, volume, "Sell")
            self.soldStocks.append(newStock)
            return newStock.uniqueId

    def buySoldStock(self, uniqueId, buyPrice):
        for index, stock in enumerate(self.soldStocks):
            if stock.uniqueId == uniqueId:
                newTotalStockValue = buyPrice * stock.volume
                borrowedCash = stock.price * stock.volume
                self.cash += borrowedCash - newTotalStockValue
                self.soldStocks.pop(index)
                return


def getVixValueConstrained(
    startDate,
    endDate,
    interval,
    belowValue=None,
    aboveValue=None,
    smoothNum=1,
    normalised=False,
):
    vixStock = StockData(
        ticker="^VIX", startDate=startDate, endDate=endDate, interval=interval
    )
    vixDataClose = vixStock.dataClose

    listIndexes = []
    newListIndexes = []
    prevValidIndex = 0

    listValues = []
    newListValues = []

    for index, dataValue in enumerate(vixDataClose):
        # If the previous correct value is equal to zero or is the previous number

        if (belowValue is not None and dataValue < belowValue) or (
            aboveValue is not None and dataValue > aboveValue
        ):
            newListIndexes.append(index)
            newListValues.append(dataValue)

        elif len(newListIndexes) != 0 and len(newListIndexes) >= smoothNum:
            smoothedListIndex = []
            smoothedListValues = []

            smoothedListIndex = newListIndexes[smoothNum - 1 :]

            if smoothNum > 1 and len(newListIndexes) > 0:
                for valueIndex in range(
                    len(newListIndexes[: len(newListIndexes) - (smoothNum - 1)])
                ):
                    newValues = newListValues[valueIndex : smoothNum + valueIndex]

                    if normalised:
                        newValues = [value / max(vixDataClose) for value in newValues]

                    valueAverage = sum(newValues) / smoothNum
                    smoothedListValues.append(valueAverage)

                listIndexes.append(smoothedListIndex)
                listValues.append(smoothedListValues)

            elif len(newListIndexes) > 0:
                if normalised:
                    newListValues = [
                        value / max(vixDataClose) for value in newListValues
                    ]
                listIndexes.append(newListIndexes)
                listValues.append(newListValues)

            newListIndexes = []
            newListValues = []

        else:
            newListIndexes = []
            newListValues = []

    return listIndexes, listValues


def plotPrice(
    company,
    startDate,
    endDate,
    interval,
    color,
    label,
    normalised=True,
    smoothNum=1,
    dayNums=None,
):
    companyStock = StockData(
        ticker=company, startDate=startDate, endDate=endDate, interval=interval
    )
    dataClose = companyStock.dataClose

    maxData = max(dataClose)
    newDayNums = []

    if normalised:
        dataClose = [(data / (maxData)) for data in dataClose]

    if smoothNum == 1:
        newDayNums = list(range(len(dataClose)))

    if smoothNum > 1:
        newDataClose = []
        for index in range(0, len(dataClose) - smoothNum):
            newData = (sum(dataClose[index : index + smoothNum])) / (smoothNum)
            if company == "^VIX" and newData < 20:
                newDataClose.append(newData)
                newDayNums.append(index)
            elif company != "^VIX" and (
                (dayNums != None and index in dayNums) or dayNums == None
            ):
                newDataClose.append(newData / 200)
                newDayNums.append(index)
        dataClose = newDataClose

    print(newDayNums)

    plt.plot(newDayNums, dataClose, label=label, color=color)

    if company == "^VIX":
        return newDayNums


def getPriceData(company, startDate, endDate, interval, color, label):
    companyStock = StockData(
        ticker=company, startDate=startDate, endDate=endDate, interval=interval
    )
    dataClose = companyStock.dataClose
    return list(range(len(dataClose)))


def plotPriceMain(
    company,
    startDate,
    endDate,
    interval,
    color,
    label,
    dayIndexes,
    smoothNum=1,
    normalised=False,
):
    companyStock = StockData(
        ticker=company, startDate=startDate, endDate=endDate, interval=interval
    )
    dataClose = companyStock.dataClose

    if normalised:
        dataClose = [value / max(dataClose) for value in dataClose]

    for indexList in dayIndexes:
        values = dataClose[indexList[0] : indexList[0] + len(indexList)]
        valuesList = []
        for index in indexList:
            valueSum = sum(dataClose[index - (smoothNum - 1) : index])
            valueAverage = valueSum / smoothNum
            valuesList.append(valueAverage)

        if indexList == dayIndexes[0]:
            plt.plot(indexList, valuesList, "g", label=label)
        else:
            plt.plot(indexList, valuesList, "g")


def plottingMain():
    # Define a start date and End Date
    startDate = dt.datetime(2021, 3, 5)
    endDate = dt.datetime.now()
    interval = "1d"

    company = "^VIX"
    dayNums = plotPrice(
        company,
        startDate,
        endDate,
        interval,
        "r",
        "Volatility Index",
        normalised=False,
        smoothNum=20,
    )

    # company = "HSI"
    # plotPrice(company, startDate, endDate, interval, "b", "Apple", normalised = False, smoothNum=20, dayNums=dayNums)

    company = "^GSPC"
    plotPrice(
        company,
        startDate,
        endDate,
        interval,
        "g",
        "S&P 500",
        normalised=False,
        smoothNum=20,
        dayNums=dayNums,
    )

    plt.legend()
    plt.show()


def plottingMain2():
    startDate = dt.datetime(2020, 1, 1)
    endDate = dt.datetime.now()
    interval = "1d"

    vixListIndexes, vixListValues = getVixValueConstrained(
        startDate,
        endDate,
        interval,
        belowValue=25,
        aboveValue=None,
        smoothNum=2,
        normalised=False,
    )

    for indexList, valueList in zip(vixListIndexes, vixListValues):
        plt.plot(indexList, valueList, "b")

    companyTickers = {
        "SP500": "^GSPC",
        "Meta": "META",
        "Apple": "AAPL",
        "HANG": "^HSI",
        "DAX": "^GDAXI",
        "Google": "GOOG",
        "Netflix": "NFLX",
        "Amazon": "AMZN",
        "Tesla": "TSLA",
        "Meta": "META",
        "FAANG+": "FNGU",
        "Peloton": "PTON",
        "SquareSpace": "SPCE",
        "Twitter": "TWTR",
        "Novo": "NVO",
    }

    ## This was over 300 days ago. No

    ## Amazon: Yes
    # Facebook: Little
    # SP500: Little
    ## Apple: Yes
    # Hang: No
    # DAX: Yes/Little
    ## Google: Yes
    ## Netflix: Yes
    ## Tesla: Yes
    # Meta: Yes

    # VIX is below 20: buy and above 25: sell -- FAANG
    # 30% for one then, and then over 3 years 100% increase.

    # company = "AAPL"
    # plotPriceMain(company, startDate, endDate, interval, "b", "AAPL", dayIndexes=vixListIndexes, smoothNum=2, normalised=False)

    # company = "HSI"
    # plotPriceMain(company, startDate, endDate, interval, "b", "AAPL", dayIndexes=vixListIndexes, smoothNum=2, normalised=False)

    text = "Novo"
    company = companyTickers[text]

    plotPriceMain(
        company,
        startDate,
        endDate,
        interval,
        "b",
        text,
        dayIndexes=vixListIndexes,
        smoothNum=2,
        normalised=False,
    )

    # company = "^GSPC"
    # plotPriceMain(company, startDate, endDate, interval, "g", "S&P 500", dayIndexes=vixListIndexes, smoothNum=2, normalised=False)

    plt.margins(x=0)
    plt.legend()
    plt.show()


def simulationMain():
    startingCash = 50000
    financialSimulation = FinancialSimulation(startingCash)

    uniqueId = financialSimulation.buyStock("FB", 10, 10)
    financialSimulation.sellBoughtStock(uniqueId, 11)

    print(financialSimulation.cash)

    uniqueId = financialSimulation.sellStock("FB", 11, 10)

    financialSimulation.buySoldStock(uniqueId, 10)

    print(financialSimulation.cash)


def findGoodStocks():
    pass


def findGoodStocks(startDate, endDate):
    """
    Function to find the stock from 'tickerSymbols.csv':
    These stocks must have a:
     - 20% yearly return per year
     - 30% yearly return to date
     - 100% return over the last 3 years

    This function also calculates and returns the
    """

    # File with all stock tickers from US markets
    df = pd.read_csv("tickerSymbols.csv")

    dateDelta = endDate - startDate

    if dateDelta.days < 1095:
        print(
            "================================================================================\nERROR\nThe start and end dates are too close together\nCurrently the two dates are {} days apart, however they need to be at least 1095 days apart".format(
                dateDelta.days
            )
        )
        return {}

    interval = "1d"
    fig, ax = plt.subplots(nrows=3, ncols=3)
    subFigureNumX = 0
    subFigureNumY = 0
    goodStockNum = 0
    returnOnInvestment = {}

    for index, row in list(df.iterrows()):

        company = row["Symbol"]
        label = row["Name"]
        companyStock = StockData(
            ticker=company, startDate=startDate, endDate=endDate, interval=interval
        )
        close = companyStock.dataClose
        high = companyStock.dataHigh
        low = companyStock.dataLow

        if high != None and len(high) >= 1095:
            print(
                "Company:",
                company,
                "|| Good Companies Found:",
                goodStockNum,
                "|| Total Companies Filtered:",
                index,
            )

            # Redefining important values
            maxH = max(high)
            cH = high[-1]
            yOneH = high[-365]
            yTwoH = high[-730]
            yThreeH = high[-1095]

            if (
                (cH * 1.02) >= maxH
                and maxH >= (yOneH * 1.3)
                and (yOneH >= yTwoH * 1.2)
                and yTwoH >= (yThreeH * 1.2)
                and maxH >= (yThreeH * 2)
            ):
                print("Doubled over 3 years - Yes")
                goodStockNum += 1

                # Plotting the data on one of the subgraphs
                ax[subFigureNumY][subFigureNumX].plot(
                    range(len(high)), high, color="green", label=company
                )
                ax[subFigureNumY][subFigureNumX].legend()
                returnOnInvestment[company] = (maxH / high[0]) * 100

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

    return returnOnInvestment


if __name__ == "__main__":
    startDate = dt.datetime(2019, 1, 1)
    endDate = dt.datetime.now()

    returnOnInvestment = findGoodStocks(startDate, endDate)

    print(returnOnInvestment)

    plt.show()

    # plottingMain2()
