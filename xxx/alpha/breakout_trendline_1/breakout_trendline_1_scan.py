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
import multiprocessing
import strategy_constant
from stockstats import StockDataFrame

kite = connect.get_kite_connect_obj()
local_data = open('../../connect/base_path/local_data.txt', 'r').read()

print("multiprocessing.cpu_count(): " + str(multiprocessing.cpu_count()))
today_date = datetime.today().strftime('%Y-%m-%d')
number_of_back_market_days = strategy_constant.number_of_days_for_backtest
# scan_dates_array = ['2021-09-23']
scan_dates_array = scan_dates.get_scan_dates_array(today_date, number_of_back_market_days)
# print(scan_dates_array)
scan_stocks_array = strategy_constant.scan_stocks_array
# scan_stocks_array = scan_stocks.get_scan_stocks_array(strategy_constant.scan_stocks_category_array, 50)
# print(scan_stocks_array)


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


def get_avg_close_avg_vol(stock_symbol, sdf, i):
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
    avg_vol = sum_volume / number_of_days
    return [avg_close, avg_vol]


def print_upper_trend_lines(records, stock_symbol, nse_token, data_start_date, data_end_date):
    df = pd.DataFrame(records)
    sdf = StockDataFrame.retype(df)
    utl_details_array = []
    # Here we are not checking this till last day as last day will be checked for breakout.
    for i in range(0, sdf.index.size - 2):
        avg_close_avg_vol = get_avg_close_avg_vol(stock_symbol, sdf, i)
        avg_close = avg_close_avg_vol[0]
        avg_volume = avg_close_avg_vol[1]
        for j in range(i + 1, sdf.index.size - 1):
            utl_left_touching_date = str(sdf.index[i])[0:10]
            utl_right_touching_date = str(sdf.index[j])[0:10]
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
                "utl_left_touching_date" : utl_left_touching_date,
                "utl_right_touching_date" : utl_right_touching_date,
                "data_end_date" : data_end_date,
                "i" : i,
                "j" : j,
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
            if not sdf['volume'][sdf.index.size - 1] >= avg_volume * strategy_constant.avg_volume_multiplier:
                continue
            utl_details_array.append(utl_details)

    # for temp_utl_details in utl_details_array:
    #     print("------------------------------------------------------------------------------------------------------------------------------------------------------")
    #     print("symbol: " + method_symbol + ", date: " + method_data_end_date)
    #     print("-------------------------------------------------------------------------------------------------------")
    #     print(temp_utl_details)
    #     print("#######################################################################################################")
    #     print("######################################################################################################################################################")
    #     print()


job_details_array = []
lot_index_details_array = []


def populate_job_array():
    for scan_date in scan_dates_array:
        for scan_stock in scan_stocks_array:
            job = {
                "scan_date": scan_date,
                "symbol": scan_stock[0],
                "nse_token": scan_stock[1]
            }
            job_details_array.append(job)


def populate_job_array_and_lot_index_array():
    populate_job_array()
    total_number_of_jobs = len(job_details_array)
    number_of_lots = int(total_number_of_jobs / strategy_constant.number_of_jobs_in_one_lot)
    for lot_num in range(0, number_of_lots, 1):
        lot_index_details = {
            "lot_min_index" : strategy_constant.number_of_jobs_in_one_lot * lot_num,
            "lot_max_index" : (strategy_constant.number_of_jobs_in_one_lot * (lot_num + 1)) - 1
        }
        lot_index_details_array.append(lot_index_details)
    jobs_in_last_lot = total_number_of_jobs % strategy_constant.number_of_jobs_in_one_lot
    if jobs_in_last_lot > 0:
        lot_index_details = {
            "lot_min_index" : strategy_constant.number_of_jobs_in_one_lot * number_of_lots,
            "lot_max_index" : total_number_of_jobs - 1
        }
        lot_index_details_array.append(lot_index_details)


def main():
    populate_job_array_and_lot_index_array()
    time_till_now = 0
    lot_number = 0
    for lot_index_details in lot_index_details_array:
        lot_number = lot_number + 1
        lot_start_time = time.time()
        lot_min_index = lot_index_details['lot_min_index']
        lot_max_index = lot_index_details['lot_max_index']
        method_parameters_array = []
        historical_data_thread_array = []
        for job_details_itr in range(lot_min_index, (lot_max_index + 1), 1):
            scan_date = job_details_array[job_details_itr]['scan_date']
            symbol = job_details_array[job_details_itr]['symbol']
            nse_token = job_details_array[job_details_itr]['nse_token']
            print("scan_date: " + scan_date + ", symbol: " + symbol)

            data_end_date = date(int(scan_date[0:4]), int(scan_date[5:7]), int(scan_date[8:10]))
            data_start_date = data_end_date - timedelta(days=(strategy_constant.number_of_days_prev_data_required - 1))

            method_parameters = {
                "symbol" : symbol,
                "nse_token" : nse_token,
                "data_start_date" : str(data_start_date),
                "data_end_date" : str(data_end_date)
            }
            method_parameters_array.append(method_parameters)
            historical_data_thread = thread.ThreadWithReturnValue(target=kite.historical_data, args=(nse_token, str(data_start_date), str(data_end_date), 'day'))
            historical_data_thread.start()
            historical_data_thread_array.append(historical_data_thread)
            time.sleep(0.30)

            # print_bottom()

        start_time = time.time()
        method_itr = 0
        utl_thread_array = []
        for historical_data_thread in historical_data_thread_array:
            records = historical_data_thread.join()
            method_symbol = method_parameters_array[method_itr]['symbol']
            method_nse_token = method_parameters_array[method_itr]['nse_token']
            method_data_start_date = method_parameters_array[method_itr]['data_start_date']
            method_data_end_date = method_parameters_array[method_itr]['data_end_date']

            print("method_start...: " + str(method_itr))
            # print_upper_trend_lines(records, method_symbol, method_nse_token, method_data_start_date, method_data_end_date)
            utl_thread = multiprocessing.Process(target=print_upper_trend_lines, args=(records, method_symbol, method_nse_token, method_data_start_date, method_data_end_date))
            utl_thread.start()
            utl_thread_array.append(utl_thread)
            print("method_end=====: " + str(method_itr))
            method_itr = method_itr + 1
        # print("method_itr: " + str(method_itr))
        # print("dates_itr: " + str(dates_itr))
        # print("thread_itr: " + str(thread_itr))

        join_itr = 0
        for utl_thread in utl_thread_array:
            print("join_itr start...: " + str(join_itr))
            utl_thread.join()
            print("join_itr end=====: " + str(join_itr))
            join_itr = join_itr + 1

        end_time = time.time()
        print("scan_date: " + scan_date + ", time consumed to run: " + str(end_time - start_time))
        print()
        lot_end_time = time.time()
        lot_time_elapsed = lot_end_time - lot_start_time
        time_till_now = time_till_now + lot_time_elapsed
        print("-------------------------------------------------------------------------------")
        time_taken_per_lot = int(time_till_now / lot_number)
        print("lot_number: " + str(lot_number) + ", total_time_till_now: " + str(int(time_till_now)) + ", time_taken_per_lot: " + str(time_taken_per_lot) + ", total_number_of_lots: " + str(len(lot_index_details_array)))
        print("-------------------------------------------------------------------------------")


if __name__ == "__main__":
    main()
