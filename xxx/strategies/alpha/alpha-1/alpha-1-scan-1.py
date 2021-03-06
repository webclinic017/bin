##################################################################################
# should be run at around eod
##################################################################################
base_directory = '/home/sss/Documents/bin/xxx/'
import sys
sys.path.append(base_directory + 'strategies/util')
import time
import thread
import connect
import scan_dates
import scan_stocks
import pandas as pd
import multiprocessing
import populate_array
from stockstats import StockDataFrame
from datetime import date, datetime, timedelta

kite = connect.get_kite_connect_obj()
local_data = open(base_directory + 'connect/base_path/local_data.txt', 'r').read()
logger = connect.get_logger(local_data + '/logs/alpha-1.log')
# scan_stocks_category_array = [5, 4, 3, 2, 1]
scan_stocks_category_array = [5, 4, 3]
max_percentage_change_per_day = 0.5
avg_volume_multiplier = 1
min_wait_days_for_breakout = 10
max_allowed_upper_wick_size = 1


# is_utl_respected_between (last - 1)th business day and utl_left_touching_date
def is_utl_respected(sdf, utl_details):
    utl_points_array = utl_details['utl_points_array']
    yesterday_index = sdf.index.size - 2
    for index in range(yesterday_index, utl_details['i'], -1):
        this_index_open = sdf['open'][index]
        this_index_close = sdf['close'][index]
        this_open_close_max = max(this_index_open, this_index_close)
        if utl_points_array[index] < this_open_close_max:
            # logger.info("disrespectful_date: " + str(sdf.index[index])[0:10])
            # logger.info("disrespectful_utl_point: " + str(utl_points_array[index]))
            # # logger.info(utl_details)
            # logger.info()
            return False
    return True


def is_utl_crossed_today(sdf, utl_details):
    utl_points_array = utl_details['utl_points_array']
    today_index = sdf.index.size - 1
    today_open = sdf['open'][today_index]
    today_close = sdf['close'][today_index]
    # if today_open < utl_points_array[today_index] < today_close:
    if utl_points_array[today_index] < today_close and today_open < today_close:
        # logger.info("crossed_date: " + str(sdf.index[today_index])[0:10])
        # logger.info("crossed_utl_point: " + str(utl_points_array[today_index]))
        # # logger.info(utl_details)
        # logger.info()
        return True
    return False


def get_avg_close_avg_vol_min_vol(stock_symbol, sdf, i):
    sum_close = 0
    sum_volume = 0
    min_volume = sys.maxsize
    number_of_days = 0
    for itr in range(i, sdf.index.size - 1):
        number_of_days = number_of_days + 1
        sum_close = sum_close + sdf['close'][itr]
        sum_volume = sum_volume + sdf['volume'][itr]
        if sdf['volume'][itr] < min_volume:
            min_volume = sdf['volume'][itr]
    # Here number_of_days can't be zero as possible max value of i is (sdf.index.size - 3) and
    # this loop is running between i and (sdf.index.size - 2).
    avg_close = sum_close / number_of_days
    avg_vol = sum_volume / number_of_days
    return [avg_close, avg_vol, min_volume]


def print_upper_trend_lines(sdf, method_parameters):
    stock_symbol = method_parameters['symbol']
    nse_token = method_parameters['nse_token']
    stock_category = method_parameters['stock_category']
    data_start_date = method_parameters['data_start_date']
    data_end_date = method_parameters['data_end_date']
    sma_8 = sdf['close_8_sma']
    # logger.info("stock_symbol: " + stock_symbol)
    # logger.info(sma_8)
    utl_details_array = []
    utl_found = False
    # Here we are not checking this till last day as last day will be checked for breakout.
    for i in range(0, sdf.index.size - 2):
        if utl_found:
            continue
        avg_close_avg_vol_min_vol = get_avg_close_avg_vol_min_vol(stock_symbol, sdf, i)
        avg_close = avg_close_avg_vol_min_vol[0]
        avg_volume = avg_close_avg_vol_min_vol[1]
        min_volume = avg_close_avg_vol_min_vol[2]
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
            max_allowed_upper_wick_size_today = main_body_size * max_allowed_upper_wick_size
            fractional_upper_wick_size = upper_wick_size / main_body_size
            if upper_wick_size > max_allowed_upper_wick_size_today:
                continue

            # Here i is utl_left_touching_date.
            breakout_wait_days = (sdf.index.size - 1) - i
            wait_days_for_breakout = breakout_wait_days
            if breakout_wait_days < min_wait_days_for_breakout:
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
            if mod_of_percentage_high_diff_per_day > max_percentage_change_per_day:
                continue
            utl_points_array = [None] * sdf.index.size
            utl_points_array[i] = left_high
            utl_points_array[j] = right_high
            if i > 0:
                # logger.info("i - 1: " + str(i - 1))
                for k in range(i - 1, -1, -1):
                    # logger.info("k: " + str(k))
                    left_high = left_high - high_diff_per_day
                    utl_points_array[k] = left_high
                    # utl_points_array[k] = round(left_high, 2)
                # logger.info("")
            if j < sdf.index.size - 1:
                # logger.info("j + 1: " + str(j + 1))
                for k in range(j + 1, sdf.index.size, 1):
                    # logger.info("k: " + str(k))
                    right_high = right_high + high_diff_per_day
                    utl_points_array[k] = right_high
                    # utl_points_array[k] = round(right_high, 2)
                # logger.info("")
            if j - i > 1:
                left_high = sdf['high'][i]
                right_high = sdf['high'][j]
                for k in range(i + 1, j, 1):
                    # logger.info("k: " + str(k))
                    left_high = left_high + high_diff_per_day
                    utl_points_array[k] = left_high
                    # utl_points_array[k] = round(left_high, 2)
                # logger.info("")

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
            if not volume_multiplier >= avg_volume_multiplier:
                continue
            logger.info("stock_symbol: " + stock_symbol + ", scan_date: " + data_end_date + ", avg_volume: " + str(avg_volume) + ", breakout_volume: " + str(sdf['volume'][sdf.index.size - 1]) + ", volume_multiplier: " + str(volume_multiplier))
            utl_found = True
            conn = connect.mysql_connection()
            cursor = conn.cursor()
            insert_query = "insert into alpha_1_scan_1_filtered (" \
                           "stock_category, " \
                           "stock_symbol, " \
                           "breakout_date, " \
                           "utl_left_touching_date, " \
                           "utl_right_touching_date, " \
                           "utl_left_touching_high, " \
                           "utl_right_touching_high, " \
                           "percentage_change_per_day, " \
                           "breakout_utl, " \
                           "breakout_open, " \
                           "breakout_close, " \
                           "breakout_high, " \
                           "breakout_low, " \
                           "breakout_volume, " \
                           "breakout_sma8, " \
                           "min_volume_between_utl_left_and_breakout, " \
                           "avg_volume_between_utl_left_and_breakout, " \
                           "volume_multiplier, " \
                           "wait_days_for_breakout, " \
                           "breakout_upper_wick_size" \
                           ") values ('" + \
                           stock_category + "', '" + \
                           stock_symbol + "', '" + \
                           data_end_date + "', '" + \
                           utl_left_touching_date + "', '" + \
                           utl_right_touching_date + "', '" + \
                           str(utl_points_array[i]) + "', '" + \
                           str(utl_points_array[j]) + "', '" + \
                           str(percentage_high_diff_per_day) + "', '" + \
                           str(utl_points_array[sdf.index.size - 1]) + "', '" + \
                           str(sdf['open'][sdf.index.size - 1]) + "', '" + \
                           str(sdf['close'][sdf.index.size - 1]) + "', '" + \
                           str(sdf['high'][sdf.index.size - 1]) + "', '" + \
                           str(sdf['low'][sdf.index.size - 1]) + "', '" + \
                           str(sdf['volume'][sdf.index.size - 1]) + "', '" + \
                           str(sma_8[sdf.index.size - 1]) + "', '" + \
                           str(min_volume) + "', '" + \
                           str(avg_volume) + "', '" + \
                           str(volume_multiplier) + "', '" + \
                           str(wait_days_for_breakout) + "', '" + \
                           str(fractional_upper_wick_size) + \
                           "');"
            # logger.info("insert query: " + insert_query)
            cursor.execute(insert_query)
            cursor.close()
            conn.commit()
            conn.close()
            utl_details_array.append(utl_details)


def is_already_scanned(cursor, job_details_array, itr):
    scan_date = job_details_array[itr]['scan_date']
    symbol = job_details_array[itr]['symbol']
    select_breakout_trendline_1_scanned = "select stock_symbol, scan_date from alpha_1_scan_1_scanned where stock_symbol = '" + symbol + "' and scan_date = '" + scan_date + "';"
    cursor.execute(select_breakout_trendline_1_scanned)
    rows = cursor.fetchall()
    if not rows:
        return False
    return True


def stock_scanned(conn, scan_date, symbol):
    cursor = conn.cursor()
    insert_breakout_trendline_1_scanned = "insert into alpha_1_scan_1_scanned (stock_symbol, scan_date) values ('" + symbol + "', '" + scan_date + "');"
    try:
        cursor.execute(insert_breakout_trendline_1_scanned)
    except:
        logger.info("error occurred during inserting stock: " + symbol + ", date: " + scan_date)
    cursor.close()
    conn.commit()


def main():
    start_date_of_scanning = datetime.today().strftime('%Y-%m-%d')
    number_of_back_market_days = 1
    scan_dates_array = scan_dates.get_valid_market_scan_dates_array(start_date_of_scanning, number_of_back_market_days)
    scan_stocks_array = scan_stocks.get_scan_stocks_array(scan_stocks_category_array, None)
    job_and_lot = populate_array.populate_job_array_and_lot_index_array(scan_dates_array, scan_stocks_array)
    job_details_array = job_and_lot['job_details_array']
    lot_index_details_array = job_and_lot['lot_index_details_array']
    # logger.info("######################################################################################################")
    # logger.info(lot_index_details_array)
    # logger.info("######################################################################################################")
    # logger.info(job_details_array)
    # return
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
                logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! stock_symbol: " + selected_jobs_array[itr]['symbol'] + ", scan_date: " + selected_jobs_array[itr]['scan_date'])
        conn_scanned_stock_insert.close()

        lot_end_time = time.time()
        lot_time_elapsed = lot_end_time - lot_start_time
        time_till_now = time_till_now + lot_time_elapsed
        if len(selected_jobs_array) > 0:
            non_false_lot_number = non_false_lot_number + 1
            time_taken_per_lot = int(time_till_now / non_false_lot_number)
            logger.info("-----------------------------------------------------------------------------------")
            logger.info("lot_number: " + str(total_lot_number) + ", total_number_of_lots: " + str(len(lot_index_details_array)) + ", time_taken_per_lot: " + str(time_taken_per_lot) + ", remaining_time: " + str((len(lot_index_details_array) - total_lot_number) * time_taken_per_lot))
            logger.info("###################################################################################")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    logger.info("alpha-1-scan-1.py started: " + str(datetime.today().strftime('%Y-%m-%d %H:%M:%S')))
    start_time = time.time()
    main()
    logger.info("alpha-1-scan-1.py ended: " + str(datetime.today().strftime('%Y-%m-%d %H:%M:%S')))
    end_time = time.time()
    logger.info("time consumed to run alpha-1-scan-1.py completely: " + str(end_time - start_time))
