import matplotlib.pyplot as plt


def plot_stocks(stock):
    subFigureNumX = 0
    subFigureNumY = 0

    for company_stock in stock:
        close = company_stock.data_close
        ticker = company_stock.ticker

        if subFigureNumX == 0 and subFigureNumY == 0:
            _, ax = plt.subplots(nrows=3, ncols=3)

        ax[subFigureNumY][subFigureNumX].plot(
            range(len(close[(-company_stock.year_count * 5) - 1 :])),
            close[(-company_stock.year_count * 5) - 1 :],
            color="green",
            label=ticker,
        )

        ax[subFigureNumY][subFigureNumX].legend()

        if subFigureNumX == 2:
            if subFigureNumY == 2:
                subFigureNumX = 0
                subFigureNumY = 0
            else:
                subFigureNumX = 0
                subFigureNumY += 1
        else:
            subFigureNumX += 1

    plt.show()
