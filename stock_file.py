import os

def write_good_stock_to_csv(stock_data):
    folder_path = os.path.dirname(os.path.realpath(__file__))
    file_name = "stock_analysis.csv"
    file_path = os.path.join(folder_path, file_name)

    with open(file_path, "w") as file:
        file.write(
            "Ticker,Five_Year_Return,First_Year_Return,Second_Year_Return,Third_Year_Return,Sharpe_Ratio,Volatility"
        )
        for good_stock in stock_data:
            file.write(f"\n{good_stock.ticker},")
            file.write(f"{round(good_stock.five_yr_return, 2)}%,")
            file.write(f"{round(good_stock.ytd_return, 2)}%,")
            for rtn in good_stock.yearly_return[1:]:
                file.write(f"{round(rtn, 2)}%,")
            file.write(f"{round(good_stock.sharpe_ratio, 3)},")
            file.write(f"{round(good_stock.volatility, 3)}")
        file.close()
