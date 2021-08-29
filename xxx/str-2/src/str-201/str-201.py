# CREATE TABLE `strategy_201_config` (
#   `id` int(11) NOT NULL,
#   `mode` varchar(16) NOT NULL,
#   `scan_start_date` char(10) DEFAULT NULL,
#   `scan_end_date` char(10) DEFAULT NULL,
#   `scan_start_time` char(8) NOT NULL,
#   `scan_end_time` char(8) DEFAULT NULL,
#   `latest_exit_time` char(8) NOT NULL,
#   `symbols` varchar(256) NOT NULL,
#   `min_category` int(11) DEFAULT NULL,
#   `max_category` int(11) DEFAULT NULL,
#   `interval_in_minutes` int(11) NOT NULL,
#   `symbol_table` varchar(32) NOT NULL,
#   `data_table` varchar(32) NOT NULL,
#   `direction` int(11) NOT NULL,
#   `signal_limit` int(11) NOT NULL,
#   `confirmation_limit` int(11) NOT NULL,
#   `target_multiplier` double(10,2) DEFAULT NULL,
#   `volume_multiplier` double(10,2) DEFAULT NULL,
#   PRIMARY KEY (`id`)
# );
# insert into strategy_201_config values('1', 'realtime', NULL, NULL, '09:15:00', NULL, '15:15:00', '', '5', '5', '5', '', '', '-1', '70', '60', '2', '0.05');
# insert into strategy_201_config values('2', 'backtest', '0', '0', '09:15:00', '09:45:00', '15:15:00', '', '5', '5', '5', '', '', '-1', '70', '60', '2', '0.05');
# insert into strategy_201_config values('3', 'realtime', NULL, NULL, '09:15:00', NULL, '15:15:00', '"ADANIPORTS", "ASIANPAINT", "AXISBANK"', '5', '5', '5', '', '', '-1', '70', '60', '2', '0.05');
# insert into strategy_201_config values('4', 'backtest', '0', '0', '09:15:00', '09:45:00', '15:15:00', '"ADANIPORTS", "ASIANPAINT", "AXISBANK"', '5', '5', '5', '', '', '-1', '70', '60', '2', '0.05');


import os
import sys
import util
import time
import getopt
import pandas as pd
from kiteconnect import KiteConnect
from stockstats import StockDataFrame
from datetime import date, datetime, timedelta

sys.path.append('../app')
import test_1
local_hi_fi = test_1.hi_fi

number_of_symbols_in_one_db_connection = 7


def get_symbol_details_array(symbols, min_category, max_category):
    symbol_details_array = []
    conn = util.mysql_connection()
    cursor = conn.cursor()
    if len(symbols) == 0:
        select_equity_stocks = "select id, symbol, industry, category, nseToken from equityStocks where nseToken is not NULL and category <= '" + str(max_category) + "' and category >= '" + str(min_category) + "';"
    else:
        symbols_str = ''
        counter = 0
        for symbol in symbols:
            symbols_str += " symbol = '" + symbol + "'"
            if counter < (len(symbols) - 1):
                symbols_str += " or"
            counter = counter + 1
        select_equity_stocks = "select id, symbol, industry, category, nseToken from equityStocks where nseToken is not NULL and" + symbols_str + ";"
    # print("select_equity_stocks: " + select_equity_stocks)
    cursor.execute(select_equity_stocks)
    for (id, symbol, industry, category, nseToken) in cursor:
        symbol_details = {"symbol": symbol, "category": category, "nseToken": nseToken}
        symbol_details_array.append(symbol_details)
    conn.close
    return symbol_details_array


def get_strategy_201_configs(argv):
    config_id = 2
    try:
        opts, args = getopt.getopt(argv, "h:c:", ["help=", "config_id="])
    except getopt.GetoptError:
        print("exception occurred")
        print('strategy-201.py -n <number_of_back_candles_to_refresh>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print('strategy-201.py -n <number_of_back_candles_to_refresh>')
            sys.exit()
        elif opt in ("-c", "--config_id"):
            config_id = int(arg)
    if config_id == 0:
        print("error: not a valid config id")
        sys.exit(2)

    mode = ''
    scan_start_date = ''
    scan_end_date = ''
    scan_date_array = []
    scan_start_time = ''
    scan_end_time = ''
    latest_exit_time = ''
    symbols_str = ''
    symbols = []
    symbol_details_array = []
    min_category = 0
    max_category = 0
    symbol_table = 'equityStocks'
    data_table = ''
    result_table = ''
    interval_in_minutes = 0
    direction = 0
    signal_limit = 0
    confirmation_limit = 0
    target_multiplier = 0
    volume_multiplier = 0

    candle_time_set = {'09:00:00', '09:05:00', '09:10:00'}
    conn1 = util.mysql_connection()
    conn2 = util.mysql_connection()
    if conn1 and conn2 is not None:
        cursor1 = conn1.cursor()
        cursor2 = conn2.cursor()
        config_fetch_query = "select * from strategy_201_config where id = " + str(config_id) + ";"
        cursor1.execute(config_fetch_query)
        for (id, mode_val, scan_start_date_val, scan_end_date_val, scan_start_time_val, scan_end_time_val,
             latest_exit_time_val, symbols_val, min_category_val, max_category_val, interval_in_minutes_val,
             symbol_table_val, data_table_val, result_table_val, direction_val, signal_limit_val, confirmation_limit_val, target_multiplier_val,
             volume_multiplier_val) in cursor1:
            mode = mode_val
            scan_start_date = scan_start_date_val
            scan_end_date = scan_end_date_val
            scan_start_time = scan_start_time_val
            scan_end_time = scan_end_time_val
            latest_exit_time = latest_exit_time_val
            symbols_str = symbols_val
            min_category = min_category_val
            max_category = max_category_val
            interval_in_minutes = interval_in_minutes_val
            symbol_table = symbol_table_val
            data_table = data_table_val
            result_table = result_table_val
            direction = direction_val
            signal_limit = signal_limit_val
            confirmation_limit = confirmation_limit_val
            target_multiplier = target_multiplier_val
            volume_multiplier = volume_multiplier_val
    try:
        if mode != 'realtime' and mode != 'backtest':
            print("mode should be either 'realtime' or 'backtest'.")
            sys.exit(2)

        today_date = datetime.today().strftime('%Y-%m-%d')
        if mode == 'realtime':
            scan_start_date = today_date
            scan_end_date = today_date
        d_start = date(int(scan_start_date[0:4]), int(scan_start_date[5:7]), int(scan_start_date[8:10]))
        d_end = date(int(scan_end_date[0:4]), int(scan_end_date[5:7]), int(scan_end_date[8:10]))
        d_delta = d_end - d_start
        if d_start > d_end:
            print("scan_end_date should be greater than or equal to scan_start_date.")
            sys.exit(2)
        for i in range(d_delta.days + 1):
            day = d_end - timedelta(days=i)
            scan_date_array.append(str(day))

        interval_str = ''
        if interval_in_minutes == 1:
            interval_str = 'minute'
        else:
            interval_str = str(interval_in_minutes) + 'minute'
        fetch_all_timings = "select data_interval, time from data_timing where data_interval = '" + interval_str + "';"
        cursor1.execute(fetch_all_timings)
        for (data_interval, time_val) in cursor1:
            candle_time_set.add(time_val)
        if mode == 'realtime' and (scan_end_time is None or scan_end_time == ''):
            scan_end_time = datetime.today().strftime('%H:%M:00')
        if scan_start_time not in candle_time_set:
            print("scan_start_time is invalid.")
            sys.exit(2)
        if mode == 'backtest' and scan_end_time not in candle_time_set:
            print("scan_end_time is invalid.")
            sys.exit(2)
        if latest_exit_time not in candle_time_set:
            print("largest_exit_time is invalid.")
            sys.exit(2)
        # t_start = datetime(int(today_date[0:4]), int(today_date[5:7]), int(today_date[8:10]), int(scan_start_time[0:2]), int(scan_start_time[3:5]), int(scan_start_time[6:8]))
        # t_end = datetime(int(today_date[0:4]), int(today_date[5:7]), int(today_date[8:10]), int(scan_end_time[0:2]), int(scan_end_time[3:5]), int(scan_end_time[6:8]))
        # t_exit = datetime(int(today_date[0:4]), int(today_date[5:7]), int(today_date[8:10]), int(latest_exit_time[0:2]), int(latest_exit_time[3:5]), int(latest_exit_time[6:8]))
        # print("t_start: " + str(t_start))
        # print("t_end: " + str(t_end))
        # print("t_exit: " + str(t_exit))
        # if t_start > t_end:
        #     print("scan_start_time can't be greater than scan_end_time.")
        #     sys.exit(2)
        # if t_start > t_exit or t_end > t_exit:
        #     print("scan_start_time or scan_end_time can't be greater than largest_exit_time.")
        #     sys.exit(2)

        if symbols_str != '':
            symbols = symbols_str.split(',')
            for symbol in symbols:
                symbol = symbol.strip()
        if min_category < 1 or min_category > 5:
            print("invalid min_category.")
            sys.exit(2)
        if max_category < 1 or max_category > 5:
            print("invalid max_category.")
            sys.exit(2)
        if min_category > max_category:
            print("min_category can't be greater than max_category.")
            sys.exit(2)
        if interval_in_minutes != 5:
            print("invalid invterval.")
            sys.exit(2)
        if symbol_table is None or symbol_table == '':
            symbol_table = 'equityStocks'
        if interval_in_minutes == 1:
            data_table = 'minute_data'
        else:
            data_table = str(interval_in_minutes) + 'minute_data'

        if result_table == '' or result_table == None:
            print("invalid result table.")
            sys.exit(2)
        result_table_exist_query = "SHOW TABLES LIKE '" + result_table + "';"
        cursor1.execute(result_table_exist_query)
        result_table_exist_row = cursor1.fetchone()
        if result_table_exist_row is None:
            create_result_table_query = "CREATE TABLE " + result_table + " (id int(11) NOT NULL AUTO_INCREMENT, config_id int NOT NULL, symbol varchar(32) NOT NULL, date char(10) NOT NULL, signal_timestamp varchar(32) NOT NULL, position_timestamp varchar(32) NOT NULL, position_price double(16, 2) NOT NULL, volume BIGINT NOT NULL, direction INT NOT NULL, stoploss double(16, 2) NOT NULL, target double(16, 2) NOT NULL, exit_timestamp varchar(32) NOT NULL, exit_price double(16, 2) NOT NULL, profit_loss_dir INT NOT NULL, profit_loss double(16, 2) NOT NULL, PRIMARY KEY (id), KEY index_config_id (config_id), KEY index_symbol (symbol), KEY index_date (date));"
            cursor2.execute(create_result_table_query)

        if direction != 1 and direction != -1:
            print("direction is invalid.")
            sys.exit(2)
        if signal_limit < 0 or signal_limit > 100:
            print("signal_limit invalid.")
            sys.exit(2)
        if confirmation_limit < 0 or confirmation_limit > 100:
            print("confirmation_limit invalid.")
            sys.exit(2)
        if direction == 1 and confirmation_limit < signal_limit:
            print("for expected growth, confirmation_limit can't be less than signal_limit.")
            sys.exit(2)
        if direction == -1 and confirmation_limit > signal_limit:
            print("for expected fall, signal_limit can't be less than confirmation_limit.")
            sys.exit(2)
    except:
        print("exception occurred during assigning config values.")
        sys.exit(2)
    symbol_details_array = get_symbol_details_array(symbols, min_category, max_category)
    return config_id, mode, scan_date_array, scan_start_time, scan_end_time, latest_exit_time, symbol_details_array, min_category, max_category, interval_in_minutes, symbol_table, data_table, result_table, direction, signal_limit, confirmation_limit, target_multiplier, volume_multiplier


def data_analysis_and_db_update(symbol_details_array, symbol_start_index, symbol_end_index, scan_date, scan_start_time, scan_end_time, latest_exit_time, data_table, mode, direction, volume_multiplier, target_multiplier, conn1, cursor1):
    for idx in range(symbol_start_index, symbol_end_index):
        symbol_details = symbol_details_array[idx]
        time0 = time.time()
        d_this = date(int(scan_date[0:4]), int(scan_date[5:7]), int(scan_date[8:10]))
        back_days = timedelta(12)
        d_back = d_this - back_days
        back_day_scan_start_timestamp = str(d_back) + " " + scan_start_time
        this_day_scan_start_timestamp = scan_date + " " + scan_start_time
        this_day_scan_end_timestamp = scan_date + " " + scan_end_time
        this_day_scan_day_end_timestamp = scan_date + " " + latest_exit_time
        symbol_data_query = "select * from " + data_table + " where symbol = '" + symbol_details[
            'symbol'] + "' and candle_timestamp >= '" + back_day_scan_start_timestamp + "' and candle_timestamp <= '" + this_day_scan_day_end_timestamp + "';"
        cursor1.execute(symbol_data_query)
        time1 = time.time()
        df = pd.DataFrame({'open': [], 'close': [], 'low': [], 'high': [], 'volume': []}, index=[])
        time_10 = time.time()
        time_14 = 0
        for (symbol_val, count_val, date_val, time_val, candle_timestamp_val, open_val, close_val, high_val, low_val,
             Volume_val) in cursor1:
            for_loop_statement_time = 0
            if time_14 == 0:
                for_loop_statement_time = time_10
            else:
                for_loop_statement_time = time_14
            time_11 = time.time()
            row = pd.DataFrame({'open': [open_val], 'close': [close_val], 'low': [low_val], 'high': [high_val],
                                'volume': [Volume_val]}, index=[str(candle_timestamp_val)])
            time_12 = time.time()
            df = pd.concat([df, row])
            time_13 = time.time()
            # print("time11 - time10: " + str(time_11 - for_loop_statement_time))
            # print("time12 - time11: " + str(time_12 - time_11))
            # print("time13 - time12: " + str(time_13 - time_12))
            # print()
            time_14 = time.time()
        time2 = time.time()
        sdf = StockDataFrame.retype(df)
        sma_44 = sdf['close_44_sma']
        ema_55 = sdf['close_55_ema']
        rsi_14 = sdf['rsi_14']
        time3 = time.time()
        scan_start_index = 0
        for index in range(0, len(sdf.index)):
            if sdf.index[index] == this_day_scan_start_timestamp:
                scan_start_index = index
                break
        scan_end_index = 0
        if scan_start_index != 0:
            for index in range(scan_start_index, len(sdf.index)):
                if sdf.index[index] == this_day_scan_end_timestamp:
                    scan_end_index = index
                    break
        signal_timestamp = ''
        signal_index = -1
        confirmation_timestamp = ''
        confirmation_index = -1
        exit_timestamp = ''
        position_price = -1
        volume = 1000
        stoploss = -1
        target = -1
        exit_price = -1
        profit_loss = 0
        print("scan_start_index: " + str(scan_start_index))
        print("scan_end_index: " + str(scan_end_index))
        if scan_end_index != 0:
            for index in range(scan_start_index, scan_end_index + 1):
                if sdf['rsi_14'][index] > 70:
                    signal_timestamp = sdf.index[index]
                    signal_index = index
                    break
        if signal_index != -1:
            for index in range(signal_index + 1, scan_end_index + 1):
                if sdf['rsi_14'][index] < 60:
                    confirmation_timestamp = sdf.index[index]
                    confirmation_index = index
                    position_price = sdf['close'][index]
                    if direction == -1:
                        stoploss = sdf['high'][index]
                        target = position_price - (sdf['high'][index] - position_price) * target_multiplier
                    else:
                        stoploss = sdf['low'][index]
                        target = position_price + (position_price - sdf['low'][index]) * target_multiplier
                    break
        print("time1 - time0: " + str(time1 - time0))
        print("time2 - time1: " + str(time2 - time1))
        print("time3 - time2: " + str(time3 - time2))
        if confirmation_index != -1:
            volume_query = "select symbol, time, volume_avg, later_half_volume_avg from 5minute_data_volume_avg where symbol = '" + str(
                symbol_details['symbol']) + "' and time = '" + confirmation_timestamp[11:19] + "';"
            print("volume_query: " + volume_query)
            cursor1.execute(volume_query)
            volume_row = cursor1.fetchone()
            total_avg_vol = 0
            total_cur_vol = 0
            if volume_row is not None:
                total_avg_vol = volume_row[3]
            total_cur_vol = sdf['volume'][confirmation_index]
            total_min_vol = total_cur_vol
            if total_min_vol > total_avg_vol:
                total_min_vol = total_avg_vol
            volume = total_min_vol * volume_multiplier
            if mode == "backtest":
                for index in range(confirmation_index + 1, len(sdf.index)):
                    if sdf['low'][index] < target:
                        exit_timestamp = sdf.index[index]
                        exit_price = target
                        break
                    if sdf['high'][index] > stoploss:
                        exit_timestamp = sdf.index[index]
                        exit_price = stoploss
                        break
                if exit_price == -1:
                    exit_timestamp = sdf.index[len(sdf.index) - 1]
                    exit_price = (sdf['high'][len(sdf.index) - 1] + sdf['low'][len(sdf.index) - 1]) / 2
                if direction == -1:
                    profit_loss = (position_price - exit_price) * volume
                else:
                    profit_loss = (exit_price - position_price) * volume
            time4 = time.time()
            print("time4 - time3: " + str(time4 - time3))
            print("symbol: " + symbol_details[
                'symbol'] + ", signal_timestamp: " + signal_timestamp + ", position_timestamp: " + confirmation_timestamp + ", position_price: " + str(
                position_price) + ", volume: " + str(volume) + ", direction: " + str(direction) + ", stoploss: " + str(
                stoploss) + ", target: " + str(target) + ", exit_timestamp: " + exit_timestamp + ", exit_price: " + str(
                exit_price) + ", profit_loss: " + str(profit_loss))
        print('--------------------------------------------------------------------------')
    print('==========================================================================')


# def main(argv):
#     mode, scan_date_array, scan_start_time, scan_end_time, latest_exit_time, symbol_details_array, min_category, max_category, interval_in_minutes, symbol_table, data_table, direction, signal_limit, confirmation_limit, target_multiplier, volume_multiplier = get_strategy_201_configs(argv)
#     for scan_date in scan_date_array:
#         symbol_details_array_length = len(symbol_details_array)
#         symbol_processing_thread_array = []
#         symbol_processing_index = 0
#         while symbol_processing_index <= symbol_details_array_length:
#             start_index = symbol_processing_index
#             end_index = 0
#             if symbol_processing_index + number_of_symbols_in_one_db_connection <= symbol_details_array_length:
#                 end_index = symbol_processing_index + number_of_symbols_in_one_db_connection
#             else:
#                 end_index = symbol_details_array_length
#             conn1 = util.mysql_connection()
#             cursor1 = conn1.cursor()
#             symbol_processing_thread = util.ThreadWithReturnValue(target=data_analysis_and_db_update,
#                                                                 args=(symbol_details_array, start_index, end_index, scan_date, scan_start_time, scan_end_time, latest_exit_time,
#                                         data_table, mode, direction, volume_multiplier, target_multiplier, conn1, cursor1))
#             symbol_processing_thread.start()
#             symbol_processing_thread_array.append(symbol_processing_thread)
#             symbol_processing_index += number_of_symbols_in_one_db_connection
#             conn1.close
#         for symbol_processing_thread in symbol_processing_thread_array:
#             symbol_processing_thread.join()


def update_signals_in_db(historical_data_thread_array, start_index, end_index, symbol_details_array, this_day_scan_start_timestamp, this_day_scan_end_timestamp, this_day_scan_day_end_timestamp, mode, direction, target_multiplier, volume_multiplier, config_id, db_update_conn, db_update_cursor, result_table):
    target_multiplier = 1
    this_day_date = this_day_scan_start_timestamp[0:10]
    this_day_scan_start_timestamp += "+05:30"
    this_day_scan_end_timestamp += "+05:30"
    this_day_scan_day_end_timestamp += "+05:30"
    symbol_details_index = 0
    for i in range(start_index, end_index):
        symbol_details_final_index = start_index + symbol_details_index
        symbol_details = symbol_details_array[symbol_details_final_index]
        symbol_details_index += 1
        symbol = symbol_details['symbol']
        category = symbol_details['category']
        nseToken = symbol_details['nseToken']
        historical_data_thread = historical_data_thread_array[i]
        df = pd.DataFrame(historical_data_thread.join())
        sdf = StockDataFrame.retype(df)
        rsi_14 = sdf['rsi_14']
        time3 = time.time()
        scan_start_index = 0
        for index in range(0, len(sdf.index)):
            # print("sdf.index[index]: " + str(sdf.index[index]))
            # print("this_day_scan_start_timestamp: " + this_day_scan_start_timestamp)
            if str(sdf.index[index]) == this_day_scan_start_timestamp:
                scan_start_index = index
                break
        scan_end_index = 0
        if scan_start_index != 0:
            for index in range(scan_start_index, len(sdf.index)):
                if str(sdf.index[index]) == this_day_scan_end_timestamp:
                    scan_end_index = index
                    break
        day_exit_index = 0
        for index in range(0, len(sdf.index)):
            if str(sdf.index[index]) == this_day_scan_day_end_timestamp:
                day_exit_index = index
                break
        signal_timestamp = ''
        signal_index = -1
        confirmation_timestamp = ''
        confirmation_index = -1
        exit_timestamp = ''
        position_price = -1
        volume = 1000
        stoploss = -1
        target = -1
        exit_price = -1
        profit_loss = 0
        # print("scan_start_index: " + str(scan_start_index))
        # print("scan_end_index: " + str(scan_end_index))
        if scan_end_index != 0:
            for index in range(scan_start_index, scan_end_index + 1):
                if sdf['rsi_14'][index] > 70:
                    signal_timestamp = str(sdf.index[index])
                    signal_index = index
                    break
        if signal_index != -1:
            for index in range(signal_index + 1, scan_end_index + 1):
                if sdf['rsi_14'][index] < 60:
                    confirmation_timestamp = str(sdf.index[index])
                    confirmation_index = index
                    position_price = sdf['close'][index]
                    if direction == -1:
                        stoploss = sdf['high'][index]
                        target = position_price - (sdf['high'][index] - position_price) * target_multiplier
                    else:
                        stoploss = sdf['low'][index]
                        target = position_price + (position_price - sdf['low'][index]) * target_multiplier
                    break
        if confirmation_index != -1:
            volume_query = "select symbol, time, volume_avg, later_half_volume_avg from 5minute_data_volume_avg where symbol = '" + str(
                symbol_details['symbol']) + "' and time = '" + confirmation_timestamp[11:19] + "';"
            # print("volume_query: " + volume_query)
            db_update_cursor.execute(volume_query)
            volume_row = db_update_cursor.fetchone()
            total_avg_vol = 0
            total_cur_vol = 0
            if volume_row is not None:
                total_avg_vol = volume_row[3]
            total_cur_vol = sdf['volume'][confirmation_index]
            total_min_vol = total_cur_vol
            if total_min_vol > total_avg_vol:
                total_min_vol = total_avg_vol
            volume = int(total_min_vol * volume_multiplier)
            if mode == "backtest":
                for index in range(confirmation_index + 1, len(sdf.index)):
                    if sdf['low'][index] < target:
                        exit_timestamp = str(sdf.index[index])
                        exit_price = target
                        break
                    if sdf['high'][index] > stoploss:
                        exit_timestamp = str(sdf.index[index])
                        exit_price = stoploss
                        break
                if exit_price == -1:
                    exit_timestamp = str(sdf.index[day_exit_index])
                    exit_price = (sdf['high'][day_exit_index] + sdf['low'][day_exit_index]) / 2
                    # exit_timestamp = sdf.index[len(sdf.index) - 1]
                    # exit_price = (sdf['high'][len(sdf.index) - 1] + sdf['low'][len(sdf.index) - 1]) / 2
                if direction == -1:
                    profit_loss = (position_price - exit_price) * volume
                else:
                    profit_loss = (exit_price - position_price) * volume
                profit_loss_dir = -1
                if profit_loss > 0:
                    profit_loss_dir = 1
            insert_result_query = "insert into " + result_table + " (config_id, symbol, date, signal_timestamp, position_timestamp, position_price, volume, direction, stoploss, target, exit_timestamp, exit_price, profit_loss_dir, profit_loss) values('" + config_id + "', '" + symbol_details['symbol'] + "', '" + this_day_date + "', '" + signal_timestamp + "', '" + confirmation_timestamp + "', '" + position_price + "', '" + str(volume) + "', '" + str(direction) + "', '" + str(stoploss) + "', '" + str(target) + "', '" + exit_timestamp + "', '" + str(exit_price) + "', '" + str(profit_loss_dir) + "', '" + str(profit_loss) + "');"
            print(insert_result_query)
            # print("symbol: " + symbol_details[
            #     'symbol'] + ", signal_timestamp: " + signal_timestamp + ", position_timestamp: " + confirmation_timestamp + ", position_price: " + str(
            #     position_price) + ", volume: " + str(volume) + ", direction: " + str(direction) + ", stoploss: " + str(
            #     stoploss) + ", target: " + str(target) + ", exit_timestamp: " + exit_timestamp + ", exit_price: " + str(
            #     exit_price) + ", profit_loss_dir: " + str(profit_loss_dir) + ", profit_loss: " + str(profit_loss))
        # print('--------------------------------------------------------------------------')
    db_update_conn.close

def main(argv):
    api_key = open(util.baby_0_dir + "txt/api_key.txt", 'r').read()
    api_secret = open(util.baby_0_dir + "txt/api_secret.txt", 'r').read()
    access_token = open(util.baby_0_dir + "txt/access_token.txt", 'r').read()
    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)
    config_id, mode, scan_date_array, scan_start_time, scan_end_time, latest_exit_time, symbol_details_array, min_category, max_category, interval_in_minutes, symbol_table, data_table, result_table, direction, signal_limit, confirmation_limit, target_multiplier, volume_multiplier = get_strategy_201_configs(argv)
    interval = ''
    if interval_in_minutes == 1:
        interval = 'minute'
    else:
        interval = str(interval_in_minutes) + 'minute'
    for scan_date in scan_date_array:
        # print("scan_date: " + scan_date)
        d_this = date(int(scan_date[0:4]), int(scan_date[5:7]), int(scan_date[8:10]))
        back_days = timedelta(7)
        d_back = d_this - back_days
        back_day_scan_start_timestamp = str(d_back) + " " + "00:00:00"
        this_day_scan_start_timestamp = scan_date + " " + scan_start_time
        this_day_scan_end_timestamp = scan_date + " " + scan_end_time
        this_day_scan_day_end_timestamp = scan_date + " " + latest_exit_time
        this_day_day_end_timestamp = scan_date + " " + "23:59:59"
        historical_data_thread_array = []
        for i in range(0, len(symbol_details_array)):
            symbol_details = symbol_details_array[i]
            # print("symbol: " + symbol_details['symbol'])
            historical_data_thread = util.ThreadWithReturnValue(target=kite.historical_data, args=(symbol_details['nseToken'], back_day_scan_start_timestamp, this_day_day_end_timestamp, interval))
            historical_data_thread.start()
            historical_data_thread_array.append(historical_data_thread)
            time.sleep(0.15)

        db_update_thread_array = []
        data_thread_array_length = len(historical_data_thread_array)
        data_thread_processing_index = 0
        while data_thread_processing_index <= data_thread_array_length:
            start_index = data_thread_processing_index
            end_index = 0
            if data_thread_processing_index + number_of_symbols_in_one_db_connection <= data_thread_array_length:
                end_index = data_thread_processing_index + number_of_symbols_in_one_db_connection
            else:
                end_index = data_thread_array_length
            db_update_conn = util.mysql_connection()
            db_update_cursor = db_update_conn.cursor()
            db_update_thread = util.ThreadWithReturnValue(target=update_signals_in_db,
                                                                args=(historical_data_thread_array, start_index, end_index, symbol_details_array, this_day_scan_start_timestamp, this_day_scan_end_timestamp, this_day_scan_day_end_timestamp, mode, direction, target_multiplier, volume_multiplier, config_id, db_update_conn, db_update_cursor, result_table))
            db_update_thread.start()
            db_update_thread_array.append(db_update_thread)
            data_thread_processing_index += number_of_symbols_in_one_db_connection

        for db_update_thread in db_update_thread_array:
            db_update_thread.join()


if __name__ == "__main__":
    start_time = time.time()
    main(sys.argv[1:])
    end_time = time.time()
    print("time consumed to run: " + str(end_time - start_time))
