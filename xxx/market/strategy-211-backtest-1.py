import sys
import util
import time
import pytz
import getopt
import logging
from dateutil.tz import gettz
import pandas as pd
from kiteconnect import KiteConnect
from stockstats import StockDataFrame
from datetime import date, datetime, timedelta


logger = util.get_logger(util.baby_0_dir + 'txt/strategy-211.log')
kite = util.get_kite()


def has_crossed_upward_today(sdf, ema_55, rsi_14):
    crossing_condition = 0
    is_crossed_upward_today = False
    last_index = len(sdf.index) - 1

    today_avg = (sdf['close'][last_index] + sdf['open'][last_index]) / 2
    yesterday_avg = (sdf['close'][last_index - 1] + sdf['open'][last_index - 1]) / 2
    day_before_yesterday_avg = (sdf['close'][last_index - 2] + sdf['open'][last_index - 2]) / 2

    if sdf['open'][last_index] < ema_55[last_index] < sdf['close'][last_index]:
        is_crossed_upward_today = True
        crossing_condition = 1

    # As yesterday's rsi was less than limit and today's is more than limit, then definitely price has increased. No need to check.
    if ema_55[last_index] < sdf['open'][last_index] < sdf['close'][last_index] and sdf['open'][last_index - 1] < ema_55[last_index - 1] < sdf['close'][last_index - 1]:
    # if ema_55[last_index] < sdf['open'][last_index] < sdf['close'][last_index] and (sdf['open'][last_index - 1] < ema_55[last_index - 1] < sdf['close'][last_index - 1] and rsi_14[last_index - 1] <= util.strategy_211_rsi_upper_limit):
        is_crossed_upward_today = True
        crossing_condition = 2

    if ema_55[last_index] < sdf['open'][last_index] < sdf['close'][last_index] and sdf['open'][last_index - 1] < sdf['close'][last_index - 1] < ema_55[last_index - 1]:
        is_crossed_upward_today = True
        crossing_condition = 3

    return is_crossed_upward_today, crossing_condition


def has_crossed_downward_today(sdf, ema_55, rsi_14):
    crossing_condition = 0
    is_crossed_downward_today = False
    last_index = len(sdf.index) - 1

    today_avg = (sdf['close'][last_index] + sdf['open'][last_index]) / 2
    yesterday_avg = (sdf['close'][last_index - 1] + sdf['open'][last_index - 1]) / 2
    day_before_yesterday_avg = (sdf['close'][last_index - 2] + sdf['open'][last_index - 2]) / 2

    if sdf['open'][last_index] > ema_55[last_index] > sdf['close'][last_index]:
        is_crossed_downward_today = True
        crossing_condition = 1

    # As yesterday's rsi was less than limit and today's is more than limit, then definitely price has increased. No need to check.
    if ema_55[last_index] > sdf['open'][last_index] > sdf['close'][last_index] and sdf['open'][last_index - 1] > ema_55[last_index - 1] > sdf['close'][last_index - 1]:
    # if ema_55[last_index] > sdf['open'][last_index] > sdf['close'][last_index] and (sdf['open'][last_index - 1] > ema_55[last_index - 1] > sdf['close'][last_index - 1] and rsi_14[last_index - 1] >= util.strategy_211_rsi_lower_limit):
        is_crossed_downward_today = True
        crossing_condition = 2

    if ema_55[last_index] > sdf['open'][last_index] > sdf['close'][last_index] and sdf['open'][last_index - 1] > sdf['close'][last_index - 1] > ema_55[last_index - 1]:
        is_crossed_downward_today = True
        crossing_condition = 3

    return is_crossed_downward_today, crossing_condition


def fetch_data_and_scan(kite, symbol_details, from_date, to_date, to_time, yesterday_date, interval, today_records):
    conn = util.mysql_connection()
    cursor = conn.cursor()
    select_query = "select * from strategy_211_backtest_1 where symbol = '" + symbol_details['symbol'] + "' and date = '" + to_date + "';"
    cursor.execute(select_query)
    symbol_date_data = cursor.fetchone()
    if symbol_date_data is not None:
        logger.info("symbol: " + symbol_details['symbol'] + ", date: " + to_date + " already present in strategy_211_backtest_1 table.")
    else:
        to_timestamp = to_date + " " + to_time
        records = kite.historical_data(symbol_details['nseToken'], from_date, yesterday_date, interval)
        df = pd.DataFrame(records)
        # today_records = kite.historical_data(symbol_details['nseToken'], to_date + " " + "00:00:00", to_timestamp, '5minute')
        today_df = pd.DataFrame(today_records)
        # print(today_df)
        today_timestamp = pd.Timestamp(tz=gettz('Asia/Kolkata'), year=int(to_date[0:4]), month=int(to_date[5:7]), day=int(to_date[8:10]), hour=0, minute=0, second=0)
        today_open = today_df['open'][0]
        today_close = today_df['close'][len(today_df.index) - 2]
        today_high = -20000000
        today_low = 20000000
        today_volume = 0
        for i in range(0, len(today_df.index) - 1):
            # today_close = today_df['close'][i]
            if today_high < today_df['high'][i]:
                today_high = today_df['high'][i]
            if today_low > today_df['low'][i]:
                today_low = today_df['low'][i]
            today_volume += today_df['volume'][i]
        # print("today_timestamp: " + str(today_timestamp) + ", today_open: " + str(today_open) + ", today_high: " + str(today_high) + ", today_low: " + str(today_low) + ", today_close: " + str(today_close) + ", today_volume: " + str(today_volume))
        df.loc[len(df.index)] = [today_timestamp, today_open, today_high, today_low, today_close, today_volume]
        # print(df)
        sdf = StockDataFrame.retype(df)
        # if len(sdf.index) == 0:
        #     logger.info("symbol: " + symbol_details['symbol'] + ", NULLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL")
        ema_55 = sdf['close_55_ema']
        rsi_14 = sdf['rsi_14']
        is_a_signal = False
        crossing_condition = 0
        last_index = len(sdf.index) - 1
        timestamp_today = sdf.index[last_index]
        rsi_14_today = rsi_14[last_index]
        ema_55_today = ema_55[last_index]
        # logger.info("symbol: " + symbol_details['symbol'] + ", category: " + str(symbol_details['category']) + ", rsi_14_today: " + str(rsi_14_today) + ", ema_55_today: " + str(ema_55_today))
        if rsi_14[last_index] > util.strategy_211_rsi_upper_limit or rsi_14[last_index] < util.strategy_211_rsi_lower_limit:
            is_a_signal = True
        is_blocked = 0
        direction = 0
        if is_a_signal and rsi_14[last_index] > util.strategy_211_rsi_upper_limit:
            is_a_signal, crossing_condition = has_crossed_upward_today(sdf, ema_55, rsi_14)
            if is_a_signal:
                direction = 1
                # logger.info("symbol: " + symbol_details['symbol'] + ", category: " + str(symbol_details['category']) + ", crossing_condition: " + str(crossing_condition) + ", ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        if is_a_signal and rsi_14[last_index] < util.strategy_211_rsi_lower_limit:
            is_a_signal, crossing_condition = has_crossed_downward_today(sdf, ema_55, rsi_14)
            if is_a_signal:
                direction = -1
                # logger.info("symbol: " + symbol_details['symbol'] + ", category: " + str(symbol_details['category']) + ", crossing_condition: " + str(crossing_condition) + ", -----------------------------")
        if is_a_signal:
            position_price = sdf['close'][last_index]
            till_now_high = sdf['high'][last_index]
            till_now_low = sdf['low'][last_index]
            if position_price > util.stock_max_allowed_price:
                is_blocked = 1
            position_volume = -1
            avg_vol_per_min = ((sdf['volume'][last_index - 1] + sdf['volume'][last_index - 2] + sdf['volume'][last_index - 3] + sdf['volume'][last_index - 4] + sdf['volume'][last_index - 5]) / 5) / 375
            if avg_vol_per_min > util.strategy_211_min_per_minute_trade:
                avg_amount_per_min = avg_vol_per_min * position_price
                if avg_amount_per_min > util.strategy_211_max_amount_allowed_in_one_stock:
                    position_volume = util.strategy_211_max_amount_allowed_in_one_stock / position_price
                else:
                    position_volume = avg_vol_per_min
            if position_volume == -1:
                is_blocked = 2
            insert_query = "insert into strategy_211_backtest_1(date, symbol, category, nseToken, is_blocked, direction, confirmation_timestamp, avg_vol_per_min, position_price, position_volume, till_now_high, till_now_low) values ('" + to_date + "', '" + symbol_details['symbol'] + "', '" + str(symbol_details['category']) + "', '" + str(symbol_details['nseToken']) + "', '" + str(is_blocked) + "', '" + str(direction) + "', '" + to_timestamp + "', '" + str(avg_vol_per_min) + "', '" + str(position_price) + "', '" + str(position_volume) + "', '" + str(till_now_high) + "', '" + str(till_now_low) + "');"
            logger.info("insert_query: " + insert_query)
            cursor.execute(insert_query)
            conn.commit()
    conn.close


def create_threads(ids, from_date, to_date, to_time, yesterday_date):
    for slot_ids in ids:
        start_id = slot_ids['start']
        end_id = slot_ids['end']
        date_time_ids = to_date + "_" + to_time + "_" + str(start_id) + "_" + str(end_id)
        conn_backtested = util.mysql_connection()
        cursor_backtested = conn_backtested.cursor()
        select_backtested_dates_query = "select * from backtested_date_time_ids_strategy_211 where date_time_ids = '" + date_time_ids + "';"
        cursor_backtested.execute(select_backtested_dates_query)
        backtested_date_time_ids = cursor_backtested.fetchone()
        if backtested_date_time_ids is not None:
            logger.info(date_time_ids + " already backtested. ##################################################")
        else:
            conn = util.mysql_connection()
            cursor = conn.cursor()
            select_query = "select id, symbol, nseToken, category from equityStocks where nseToken is not NULL and symbol not like '%-BE' and id >= '" + str(
                start_id) + "' and id <= '" + str(end_id) + "';"
            # logger.info("###############################################################################################")
            logger.info("date: " + to_date + ", time: " + to_time + ", select_query: " + select_query)
            cursor.execute(select_query)
            data_analysis_thread_array = []
            symbol_details_array = []
            today_records_thread_array = []
            today_records_array = []
            for (id, symbol, nseToken, category) in cursor:
                symbol_details = {'id': id, 'symbol': symbol, 'nseToken': nseToken, 'category': category}
                symbol_details_array.append(symbol_details)
            for symbol_details in symbol_details_array:
                today_records = kite.historical_data(symbol_details['nseToken'], to_date + " " + "00:00:00", to_date + " " + to_time, '5minute')
                today_records_thread = util.ThreadWithReturnValue(target=kite.historical_data, args=(symbol_details['nseToken'], to_date + " " + "00:00:00", to_date + " " + to_time, '5minute'))
                today_records_thread.start()
                today_records_thread_array.append(today_records_thread)
                time.sleep(0.20)
            for today_records_thread in today_records_thread_array:
                today_records = today_records_thread.join()
                today_records_array.append(today_records)
            for i in range(0, len(symbol_details_array)):
                # id = symbol_details['id'][i]
                # symbol = symbol_details['symbol'][i]
                # nseToken = symbol_details['nseToken'][i]
                # category = symbol_details['category'][i]
                # check_confirmation(kite, symbol_details, interval, today_date_str, modulus_timestamp_str)
                # logger.info("symbol: " + symbol + ", from_date: " + from_date + ", to_date: " + to_date + ", to_time: " + to_time)
                data_analysis_thread = util.ThreadWithReturnValue(target=fetch_data_and_scan, args=(
                kite, symbol_details_array[i], from_date, to_date, to_time, yesterday_date, 'day', today_records_array[i]))
                data_analysis_thread.start()
                data_analysis_thread_array.append(data_analysis_thread)
                time.sleep(0.20)

            for data_analysis_thread in data_analysis_thread_array:
                data_analysis_thread.join()
            insert_backtest_date_time_ids_query = "insert into backtested_date_time_ids_strategy_211(date_time_ids) values('" + date_time_ids + "');"
            # logger.info("insert_backtest_date_time_ids_query: " + insert_backtest_date_time_ids_query)
            cursor_backtested.execute(insert_backtest_date_time_ids_query)
            conn_backtested.commit()
        conn_backtested.close


def main(argv):
    # mode = 'realtime'
    mode = 'backtest'
    backtest_dates = ['2021-06-10']
    # backtest_dates = util.get_strategy_211_scan_dates(kite, 32)
    # backtest_times = ['12:00:00']
    backtest_times = ['10:00:00', '11:00:00', '12:00:00', '13:00:00', '14:00:00', '15:00:00']
    # backtest_times = [
    #                 '09:15:00', '09:30:00', '09:45:00',
    #     '10:00:00', '10:15:00', '10:30:00', '10:45:00',
    #     '11:00:00', '11:15:00', '11:30:00', '11:45:00',
    #     '12:00:00', '12:15:00', '12:30:00', '12:45:00',
    #     '01:00:00', '01:15:00', '01:30:00', '01:45:00',
    #     '02:00:00', '02:15:00', '02:30:00', '02:45:00',
    #     '03:00:00', '03:15:00',
    # ]

    # ids = [{'start': 305, 'end': 305}]
    # ids = [{'start': 618, 'end': 618}]
    ids = [
        {'start': 1, 'end': 50}, {'start': 51, 'end': 100},
        {'start': 101, 'end': 150}, {'start': 151, 'end': 200},
        {'start': 201, 'end': 250}, {'start': 251, 'end': 300},
        {'start': 301, 'end': 350}, {'start': 351, 'end': 400},
        {'start': 401, 'end': 450}, {'start': 451, 'end': 500},
        {'start': 501, 'end': 550}, {'start': 551, 'end': 600},
        {'start': 601, 'end': 650}, {'start': 651, 'end': 700},
        {'start': 701, 'end': 757},
    ]

    if mode == 'realtime':
        backtest_dates = []
        backtest_times = []
        current_timestamp = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        to_date = (str(current_timestamp))[0:10]
        to_time = (str(current_timestamp))[11:19]
        backtest_dates.append(to_date)
        backtest_times.append(to_time)

    for backtest_date in backtest_dates:
        yesterday_date = util.get_strategy_211_yesterday_date(kite, backtest_date)
        for backtest_time in backtest_times:
            to_date = backtest_date
            to_time = backtest_time
            to_date_obj = date(int(to_date[0:4]), int(to_date[5:7]), int(to_date[8:10]))
            from_date = str(datetime.strftime(to_date_obj - timedelta(365 * 3), '%Y-%m-%d'))
            create_threads(ids, from_date, to_date, to_time, yesterday_date)
        if mode == 'backtest':
            update_remaining_day_high_low(backtest_date)


def update_remaining_day_high_low(to_date):
    conn = util.mysql_connection()
    cursor = conn.cursor()
    conn1 = util.mysql_connection()
    cursor1 = conn1.cursor()
    select_to_date_query = "select date, symbol, category, nseToken, is_blocked, direction, confirmation_timestamp, avg_vol_per_min, position_price, position_volume, till_now_high, till_now_low from strategy_211_backtest_1 where date = '" + to_date + "';"
    cursor.execute(select_to_date_query)
    for (date, symbol, category, nseToken, is_blocked, direction, confirmation_timestamp, avg_vol_per_min, position_price, position_volume, till_now_high, till_now_low) in cursor:
        start_time = confirmation_timestamp
        end_time = to_date + " " + "15:29:59"
        records = kite.historical_data(nseToken, start_time, end_time, '5minute')
        df = pd.DataFrame(records)
        sdf = StockDataFrame.retype(df)
        # logger.info(sdf)
        remaining_day_high = -20000000
        remaining_day_high_timestamp = ""
        remaining_day_low = 20000000
        remaining_day_low_timestamp = ""
        for i in range(0, len(sdf.index)):
            if sdf['high'][i] > remaining_day_high:
                remaining_day_high = sdf['high'][i]
                remaining_day_high_timestamp = (str(sdf.index[i]))[0:19]
            if sdf['low'][i] < remaining_day_low:
                remaining_day_low = sdf['low'][i]
                remaining_day_low_timestamp = (str(sdf.index[i]))[0:19]
        logger.info("date: " + date + ", symbol: " + symbol + ", start_time: " + start_time + ", end_time: " + end_time + ", remaining_day_high: " + str(remaining_day_high) + ", remaining_day_low: " + str(remaining_day_low))
        remaining_day_high_low = 0
        percentage_high_low = 0
        remaining_day_high_low_timestamp = ""
        if direction == 1:
            remaining_day_high_low = remaining_day_high
            remaining_day_high_low_timestamp = remaining_day_high_timestamp
            high_low = remaining_day_high_low - position_price
            percentage_high_low = (high_low * 100) / position_price
        elif direction == -1:
            remaining_day_high_low = remaining_day_low
            remaining_day_high_low_timestamp = remaining_day_low_timestamp
            high_low = position_price - remaining_day_high_low
            percentage_high_low = (high_low * 100) / position_price
        update_query = "update strategy_211_backtest_1 set remaining_day_high_low = '" + str(remaining_day_high_low) + "', percentage_high_low = '" + str(percentage_high_low) + "', remaining_day_high_low_timestamp = '" + remaining_day_high_low_timestamp + "' where date = '" + date + "' and symbol = '" + symbol + "';"
        logger.info("update_query: " + update_query)
        cursor1.execute(update_query)
        conn1.commit()
    conn1.close
    conn.close


if __name__ == "__main__":
    logger.info("strategy-211-backtest-1.py started: " + str(datetime.today().strftime('%Y-%m-%d %H:%M:%S')))
    start_time = time.time()
    main(sys.argv[1:])
    end_time = time.time()
    logger.info("time consumed to run strategy-211-backtest-1.py completely: " + str(end_time - start_time))
