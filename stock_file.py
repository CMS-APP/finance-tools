def write_good_stock_to_csv(stock_data):
    with open("stock_analysis.csv", "w") as file:
        file.write(
            "Ticker,Five_Year_Return,First_Year_Return,Second_Year_Return,Third_Year_Return,Sharpe_Ratio,Volatility"
        )
        for good_stock in stock_data:
            file.write(f"\n{good_stock.ticker},")
            file.write(f"{round(good_stock.five_yr_return * 100, 1)}%,")
            file.write(f"{round(good_stock.ytd_return * 100, 1)}%,")
            for rtn in good_stock.yearly_return[1:]:
                file.write(f"{rtn}%,")
            file.write(f"{round(good_stock.sharpe_ratio, 3)},")
            file.write(f"{round(good_stock.volatility, 3)}")
        file.close()
