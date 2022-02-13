##################################################################################
# should be run at around 4 PM in the evening after market
##################################################################################

from datetime import date, datetime, timedelta
import sys
sys.path.append('../util')
import connect
import scan_dates
import pandas as pd
import strategy_constant
from stockstats import StockDataFrame

kite = connect.get_kite_connect_obj()
local_data = open('../../connect/base_path/local_data.txt', 'r').read()

today_date = datetime.today().strftime('%Y-%m-%d')
number_of_back_market_days = strategy_constant.number_of_days_for_backtest
scan_dates_array = scan_dates.get_scan_dates_array(today_date, number_of_back_market_days)
scan_stocks_array = strategy_constant.scan_stocks_array


def print_top(data_start_date, data_end_date, scan_stock):
    print("===================================================================================================")
    print("data_start_date: " + str(data_start_date) + ", data_end_date: " + str(data_end_date) + ", scan_stock: " + scan_stock[0])
    print("===================================================================================================")


def print_bottom():
    print("###################################################################################################")
    print("###################################################################################################")
    print("")


def print_upper_trend_lines(stock_symbol, nse_token, data_start_date, data_end_date):
    records = kite.historical_data(nse_token, data_start_date, data_end_date, 'day')
    df = pd.DataFrame(records)
    sdf = StockDataFrame.retype(df)
    print(sdf)


for scan_date in scan_dates_array:
    for scan_stock in scan_stocks_array:
        data_end_date = date(int(scan_date[0:4]), int(scan_date[5:7]), int(scan_date[8:10]))
        data_start_date = data_end_date - timedelta(days=(strategy_constant.number_of_days_prev_data_required - 1))
        print_top(data_start_date, data_end_date, scan_stock)

        print_upper_trend_lines(scan_stock[0], scan_stock[1], str(data_start_date), str(data_end_date))

        print_bottom()
