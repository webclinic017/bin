##################################################################################
# should be run at around 4 PM in the evening after market
##################################################################################

from datetime import date, datetime, timedelta
import sys
sys.path.append('../../util')
import time
import thread
import connect
import scan_dates
import scan_stocks
import pandas as pd
import multiprocessing
import strategy_constant
import populate_array
from stockstats import StockDataFrame

kite = connect.get_kite_connect_obj()
local_data = open('../../connect/base_path/local_data.txt', 'r').read()

print("multiprocessing.cpu_count(): " + str(multiprocessing.cpu_count()))
print()
start_date_of_scanning = '2021-12-31'
# start_date_of_scanning = datetime.today().strftime('%Y-%m-%d')
number_of_back_market_days = strategy_constant.number_of_days_for_backtest
# scan_dates_array = ['2021-09-27']
scan_dates_array = scan_dates.get_valid_market_scan_dates_array(start_date_of_scanning, number_of_back_market_days)
# print(scan_dates_array)
# scan_stocks_array = strategy_constant.scan_stocks_array
scan_stocks_array = scan_stocks.get_scan_stocks_array(strategy_constant.scan_stocks_category_array, None)
# print(scan_stocks_array)


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


def print_upper_trend_lines(sdf, method_parameters):
    stock_symbol = method_parameters['symbol']
    nse_token = method_parameters['nse_token']
    data_start_date = method_parameters['data_start_date']
    data_end_date = method_parameters['data_end_date']
    sma_8 = sdf['close_8_sma']
    # print("stock_symbol: " + stock_symbol)
    # print(sma_8)
    utl_details_array = []
    utl_found = False
    # Here we are not checking this till last day as last day will be checked for breakout.
    for i in range(0, sdf.index.size - 2):
        if utl_found:
            continue
        avg_close_avg_vol = get_avg_close_avg_vol(stock_symbol, sdf, i)
        avg_close = avg_close_avg_vol[0]
        avg_volume = avg_close_avg_vol[1]
        for j in range(i + 1, sdf.index.size - 1):

            if utl_found:
                continue

            if sdf['close'][sdf.index.size - 1] < sma_8[sdf.index.size - 1]:
                continue

            # if not green then continue
            if sdf['open'][sdf.index.size - 1] > sdf['close'][sdf.index.size - 1]:
                continue

            # if its a rejection candle (green - see above condition) then continue
            upper_wick_size = sdf['high'][sdf.index.size - 1] - sdf['close'][sdf.index.size - 1]
            main_body_size = sdf['close'][sdf.index.size - 1] - sdf['open'][sdf.index.size - 1]
            if main_body_size == 0:
                continue
            max_allowed_upper_wick_size_today = main_body_size * strategy_constant.max_allowed_upper_wick_size
            fractional_upper_wick_size = upper_wick_size / main_body_size
            if upper_wick_size > max_allowed_upper_wick_size_today:
                continue

            # Here i is utl_left_touching_date.
            breakout_wait_days = (sdf.index.size - 1) - i
            wait_days_for_breakout = breakout_wait_days
            if breakout_wait_days < strategy_constant.min_wait_days_for_breakout:
                continue

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
            volume_multiplier = sdf['volume'][sdf.index.size - 1] / avg_volume
            if not volume_multiplier >= strategy_constant.avg_volume_multiplier:
                continue
            print("stock_symbol: " + stock_symbol + ", scan_date: " + data_end_date + ", avg_volume: " + str(avg_volume) + ", breakout_volume: " + str(sdf['volume'][sdf.index.size - 1]) + ", volume_multiplier: " + str(volume_multiplier))
            utl_found = True
            conn = connect.mysql_connection()
            cursor = conn.cursor()
            insert_query = "insert into breakout_trendline_1_details (stock_symbol, scan_date, utl_left_touching_date, utl_right_touching_date, utl_left_touching_value, utl_right_touching_value, avg_close, avg_volume, today_utl, today_open, today_close, today_high, today_low, today_volume, percentage_change_per_day, volume_multiplier, wait_days_for_breakout, upper_wick_size) values ('" + stock_symbol + "', '" + data_end_date + "', '" + utl_left_touching_date + "', '" + utl_right_touching_date + "', '" + str(
                utl_points_array[i]) + "', '" + str(utl_points_array[j]) + "', '" + str(avg_close) + "', '" + str(avg_volume) + "', '" + str(
                utl_points_array[sdf.index.size - 1]) + "', '" + str(sdf['open'][sdf.index.size - 1]) + "', '" + str(sdf['close'][sdf.index.size - 1]) + "', '" + str(
                sdf['high'][sdf.index.size - 1]) + "', '" + str(sdf['low'][sdf.index.size - 1]) + "', '" + str(sdf['volume'][sdf.index.size - 1]) + "', '" + str(
                percentage_high_diff_per_day) + "', '" + str(volume_multiplier) + "', '" + str(wait_days_for_breakout) + "', '" + str(fractional_upper_wick_size) + "');"
            cursor.execute(insert_query)
            cursor.close()
            conn.commit()
            conn.close()
            utl_details_array.append(utl_details)


def is_already_scanned(cursor, job_details_array, itr):
    scan_date = job_details_array[itr]['scan_date']
    symbol = job_details_array[itr]['symbol']
    select_breakout_trendline_1_scanned = "select stock_symbol, scan_date from breakout_trendline_1_scanned where stock_symbol = '" + symbol + "' and scan_date = '" + scan_date + "';"
    cursor.execute(select_breakout_trendline_1_scanned)
    rows = cursor.fetchall()
    if not rows:
        return False
    return True


def stock_scanned(conn, scan_date, symbol):
    cursor = conn.cursor()
    insert_breakout_trendline_1_scanned = "insert into breakout_trendline_1_scanned (stock_symbol, scan_date) values ('" + symbol + "', '" + scan_date + "');"
    try:
        cursor.execute(insert_breakout_trendline_1_scanned)
    except:
        print("error occurred during inserting stock: " + symbol + ", date: " + scan_date)
    cursor.close()
    conn.commit()


def main():
    job_and_lot = populate_array.populate_job_array_and_lot_index_array(scan_dates_array, scan_stocks_array)
    job_details_array = job_and_lot['job_details_array']
    lot_index_details_array = job_and_lot['lot_index_details_array']
    time_till_now = 0
    total_lot_number = 0
    non_false_lot_number = 0
    conn = connect.mysql_connection()
    cursor = conn.cursor()
    for lot_index_details in lot_index_details_array:
        lot_start_time = time.time()

        total_lot_number = total_lot_number + 1
        lot_min_index = lot_index_details['lot_min_index']
        lot_max_index = lot_index_details['lot_max_index']

        selected_jobs_array = []
        historical_data_thread_array = []
        ult_calculation_method_parameters_array = []
        for itr in range(lot_min_index, (lot_max_index + 1), 1):
            already_scanned = is_already_scanned(cursor, job_details_array, itr)
            if not already_scanned:
                populate_array.populate_historical_data_thread_and_method_parameters_array(
                    kite,
                    thread,
                    job_details_array,
                    itr,
                    historical_data_thread_array,
                    ult_calculation_method_parameters_array
                )
                selected_jobs_array.append(job_details_array[itr])

        is_data_found_for_scanning = []
        utl_calculation_thread_array = []
        for itr in range(0, len(historical_data_thread_array), 1):
            records = historical_data_thread_array[itr].join()
            df = pd.DataFrame(records)
            sdf = StockDataFrame.retype(df)
            if sdf is None or sdf.index.size == 0:
                is_data_found_for_scanning.append(0)
                # is_data_found_for_scanning.append(1)
            else:
                is_data_found_for_scanning.append(1)
            utl_thread = multiprocessing.Process(target=print_upper_trend_lines, args=(sdf, ult_calculation_method_parameters_array[itr]))
            utl_thread.start()
            utl_calculation_thread_array.append(utl_thread)

        conn_scanned_stock_insert = connect.mysql_connection()
        for itr in range(0, len(utl_calculation_thread_array), 1):
            utl_calculation_thread_array[itr].join()
            if is_data_found_for_scanning[itr] == 1:
                stock_scanned(conn_scanned_stock_insert, selected_jobs_array[itr]['scan_date'], selected_jobs_array[itr]['symbol'])
            else:
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! stock_symbol: " + selected_jobs_array[itr]['symbol'] + ", scan_date: " + selected_jobs_array[itr]['scan_date'])
        conn_scanned_stock_insert.close()

        lot_end_time = time.time()
        lot_time_elapsed = lot_end_time - lot_start_time
        time_till_now = time_till_now + lot_time_elapsed
        if len(selected_jobs_array) > 0:
            non_false_lot_number = non_false_lot_number + 1
            time_taken_per_lot = int(time_till_now / non_false_lot_number)
            print("-----------------------------------------------------------------------------------")
            print("lot_number: " + str(total_lot_number) + ", total_number_of_lots: " + str(len(lot_index_details_array)) + ", time_taken_per_lot: " + str(time_taken_per_lot) + ", remaining_time: " + str((len(lot_index_details_array) - total_lot_number) * time_taken_per_lot))
            print("###################################################################################")
            print()

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
