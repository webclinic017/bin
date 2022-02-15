##################################################################################
# should be run at around 4 PM in the evening after market
##################################################################################

from datetime import date, datetime, timedelta
import sys
sys.path.append('../util')
import time
import thread
import connect
import scan_dates
import scan_stocks
import pandas as pd
import strategy_constant
from stockstats import StockDataFrame

kite = connect.get_kite_connect_obj()
local_data = open('../../connect/base_path/local_data.txt', 'r').read()

today_date = datetime.today().strftime('%Y-%m-%d')
number_of_back_market_days = strategy_constant.number_of_days_for_backtest
scan_dates_array = scan_dates.get_scan_dates_array(today_date, number_of_back_market_days)
scan_stocks_array = scan_stocks.get_scan_stocks_array(strategy_constant.scan_stocks_category_array, 10)


def print_top(data_start_date, data_end_date, scan_stock):
    print("===================================================================================================")
    print("data_start_date: " + str(data_start_date) + ", data_end_date: " + str(data_end_date) + ", scan_stock: " + scan_stock[0])
    print("===================================================================================================")


def print_bottom():
    print("###################################################################################################")
    print("###################################################################################################")
    print("")


# is_utl_respected_between (last - 1)th business day and utl_left_touching_date
def is_utl_respected(sdf, utl_details):
    utl_points_array = utl_details['utl_points_array']
    yesterday_index = sdf.index.size - 2
    for index in range(yesterday_index, utl_details['i'], -1):
        this_index_open = sdf['open'][index]
        this_index_close = sdf['close'][index]
        this_open_close_max = max(this_index_open, this_index_close)
        if utl_points_array[index] < this_open_close_max:
            # print("disrespectful_date: " + str(sdf.index[index])[0:10])
            # print("disrespectful_utl_point: " + str(utl_points_array[index]))
            # # print(utl_details)
            # print()
            return False
    return True


def is_utl_crossed_today(sdf, utl_details):
    utl_points_array = utl_details['utl_points_array']
    today_index = sdf.index.size - 1
    today_open = sdf['open'][today_index]
    today_close = sdf['close'][today_index]
    # if today_open < utl_points_array[today_index] < today_close:
    if utl_points_array[today_index] < today_close and today_open < today_close:
        # print("crossed_date: " + str(sdf.index[today_index])[0:10])
        # print("crossed_utl_point: " + str(utl_points_array[today_index]))
        # # print(utl_details)
        # print()
        return True
    return False


def print_upper_trend_lines(records, stock_symbol, nse_token, data_start_date, data_end_date):
    df = pd.DataFrame(records)
    sdf = StockDataFrame.retype(df)
    utl_details_array = []
    # Here we are not checking this till last day as last day will be checked for breakout.
    for i in range(0, sdf.index.size - 2):
        for j in range(i + 1, sdf.index.size - 1):
            utl_left_touching_date = str(sdf.index[i])[0:10]
            utl_right_touching_date = str(sdf.index[j])[0:10]

            sum_close = 0
            sum_volume = 0
            number_of_days = 0
            for itr in range(i, sdf.index.size - 1):
                number_of_days = number_of_days + 1
                sum_close = sum_close + sdf['close'][itr]
                sum_volume = sum_volume + sdf['volume'][itr]
            # Here number_of_days can't be zero as possible max value of i is (sdf.index.size - 3) and
            # this loop is running between i and (sdf.index.size - 2).
            avg_close = sum_close / number_of_days
            avg_volume = sum_volume / number_of_days

            days_diff = j - i
            left_high = sdf['high'][i]
            right_high = sdf['high'][j]
            high_diff = right_high - left_high
            high_diff_per_day = high_diff / days_diff
            # high_diff_per_day = round((high_diff / days_diff), 2)
            percentage_high_diff_per_day = high_diff_per_day * 100 / avg_close
            mod_of_percentage_high_diff_per_day = percentage_high_diff_per_day
            if mod_of_percentage_high_diff_per_day < 0:
                mod_of_percentage_high_diff_per_day = mod_of_percentage_high_diff_per_day * -1
            if mod_of_percentage_high_diff_per_day > strategy_constant.max_percentage_change_per_day:
                continue
            utl_points_array = [None] * sdf.index.size
            utl_points_array[i] = left_high
            utl_points_array[j] = right_high
            if i > 0:
                # print("i - 1: " + str(i - 1))
                for k in range(i - 1, -1, -1):
                    # print("k: " + str(k))
                    left_high = left_high - high_diff_per_day
                    utl_points_array[k] = left_high
                    # utl_points_array[k] = round(left_high, 2)
                # print("")
            if j < sdf.index.size - 1:
                # print("j + 1: " + str(j + 1))
                for k in range(j + 1, sdf.index.size, 1):
                    # print("k: " + str(k))
                    right_high = right_high + high_diff_per_day
                    utl_points_array[k] = right_high
                    # utl_points_array[k] = round(right_high, 2)
                # print("")
            if j - i > 1:
                left_high = sdf['high'][i]
                right_high = sdf['high'][j]
                for k in range(i + 1, j, 1):
                    # print("k: " + str(k))
                    left_high = left_high + high_diff_per_day
                    utl_points_array[k] = left_high
                    # utl_points_array[k] = round(left_high, 2)
                # print("")

            utl_details = {
                "stock" : stock_symbol,
                "data_start_date" : data_start_date,
                "data_end_date" : data_end_date,
                "i" : i,
                "j" : j,
                "utl_left_touching_date" : utl_left_touching_date,
                "utl_right_touching_date" : utl_right_touching_date,
                "avg_close" : avg_close,
                "avg_volume" : avg_volume,
                "today_volume" : sdf['volume'][sdf.index.size - 1],
                "high_diff_per_day" : high_diff_per_day,
                "percentage_high_diff_per_day" : percentage_high_diff_per_day,
                "utl_points_array" : utl_points_array
            }
            utl_respect = is_utl_respected(sdf, utl_details)
            if not utl_respect:
                continue
            utl_crossed_today = is_utl_crossed_today(sdf, utl_details)
            if not utl_crossed_today:
                continue
            if not sdf['volume'][sdf.index.size - 1] > avg_volume * strategy_constant.avg_volume_multiplier:
                continue
            utl_details_array.append(utl_details)

    # print()
    # print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    # print()
    for temp_utl_details in utl_details_array:
        print("------------------------------------------------------------------------------------------------------------------------------------------------------")
        print("symbol: " + method_symbol + ", date: " + method_data_end_date)
        print("-------------------------------------------------------------------------------------------------------")
        print(temp_utl_details)
        print("#######################################################################################################")
        print("######################################################################################################################################################")
        print()
    # print("sdf.index.size: " + str(sdf.index.size))
    # print("total_utls: " + str(len(utl_details_array)))


method_parameters_array = []
historical_data_thread_array = []
for scan_date in scan_dates_array:
    for scan_stock in scan_stocks_array:
        data_end_date = date(int(scan_date[0:4]), int(scan_date[5:7]), int(scan_date[8:10]))
        data_start_date = data_end_date - timedelta(days=(strategy_constant.number_of_days_prev_data_required - 1))
        # print_top(data_start_date, data_end_date, scan_stock)

        method_parameters = {
            "symbol" : scan_stock[0],
            "nse_token" : scan_stock[1],
            "data_start_date" : str(data_start_date),
            "data_end_date" : str(data_end_date)
        }
        method_parameters_array.append(method_parameters)
        historical_data_thread = thread.ThreadWithReturnValue(target=kite.historical_data, args=(scan_stock[1], str(data_start_date), str(data_end_date), 'day'))
        historical_data_thread.start()
        historical_data_thread_array.append(historical_data_thread)
        time.sleep(0.15)

        # print_bottom()

method_itr = 0
for historical_data_thread in historical_data_thread_array:
    records = historical_data_thread.join()
    method_symbol = method_parameters_array[method_itr]['symbol']
    method_nse_token = method_parameters_array[method_itr]['nse_token']
    method_data_start_date = method_parameters_array[method_itr]['data_start_date']
    method_data_end_date = method_parameters_array[method_itr]['data_end_date']
    # print("------------------------------------------------------------------------------------------------------------------------------------------------------")
    # print("symbol: " + method_symbol + ", date: " + method_data_end_date)
    # print("-------------------------------------------------------------------------------------------------------")
    print_upper_trend_lines(records, method_symbol, method_nse_token, method_data_start_date, method_data_end_date)
    # print("#######################################################################################################")
    # print("######################################################################################################################################################")
    # print()
    method_itr = method_itr + 1
print("method_itr: " + str(method_itr))
