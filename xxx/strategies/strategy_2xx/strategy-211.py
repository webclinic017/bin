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
breakout_percentage = 2


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


def insert_signal_in_db_table(conn, cursor, symbol_details, sdf, last_index, strategy, direction, to_date, to_timestamp):
    is_blocked = 0
    position_price = sdf['close'][last_index]
    if position_price > util.stock_max_allowed_price:
        is_blocked = 1
    position_volume = 0
    avg_vol_per_min = 0
    if is_blocked == 0:
        avg_vol_per_min = ((sdf['volume'][last_index - 1] + sdf['volume'][last_index - 2] + sdf['volume'][
            last_index - 3] + sdf['volume'][last_index - 4] + sdf['volume'][last_index - 5]) / 5) / 375
        if avg_vol_per_min > util.strategy_211_min_per_minute_trade:
            avg_amount_per_min = avg_vol_per_min * position_price
            if avg_amount_per_min > util.strategy_211_max_amount_allowed_in_one_stock:
                position_volume = util.strategy_211_max_amount_allowed_in_one_stock / position_price
            else:
                position_volume = avg_vol_per_min
        if position_volume == 0:
            is_blocked = 2
    insert_query = "insert into strategy_211(date, symbol, category, nseToken, strategy, is_blocked, direction, confirmation_timestamp, avg_vol_per_min, position_price, position_volume) values ('" + to_date + "', '" + \
                   symbol_details['symbol'] + "', '" + str(symbol_details['category']) + "', '" + str(
        symbol_details['nseToken']) + "', '" + strategy + "', '" + str(is_blocked) + "', '" + str(
        direction) + "', '" + to_timestamp + "', '" + str(avg_vol_per_min) + "', '" + str(
        position_price) + "', '" + str(position_volume) + "');"
    logger.info("insert_query: " + insert_query)
    cursor.execute(insert_query)
    conn.commit()


def update_price_in_db(conn, cursor, symbol_date_data, sdf, symbol_details, to_date, strategy):
    direction = symbol_date_data[0]
    position_price = symbol_date_data[1]
    open_price = sdf['open'][len(sdf.index) - 1]
    high_price = sdf['high'][len(sdf.index) - 1]
    low_price = sdf['low'][len(sdf.index) - 1]
    close_price = sdf['close'][len(sdf.index) - 1]
    high_low_diff = 0
    if direction == 1:
        high_low_diff = high_price - position_price
    elif direction == -1:
        high_low_diff = position_price - low_price
    high_low_diff_percentage = (high_low_diff * 100) / position_price
    close_diff = 0
    if direction == 1:
        close_diff = close_price - position_price
    elif direction == -1:
        close_diff = position_price - close_price
    close_diff_percentage = (close_diff * 100) / position_price
    update_query = "update strategy_211 set later_high_low_percentage = '" + str(
        high_low_diff_percentage) + "', later_close_percentage = '" + str(close_diff_percentage) + "', open = '" + str(
        open_price) + "', high = '" + str(high_price) + "', low = '" + str(low_price) + "', close = '" + str(
        close_price) + "' where symbol = '" + symbol_details['symbol'] + "' and date = '" + to_date + "' and strategy = '" + strategy + "';"
    logger.info("symbol: " + symbol_details['symbol'] + ", date: " + to_date + " already present for strategy emarsi.")
    logger.info("update_query: " + update_query)
    cursor.execute(update_query)
    conn.commit()


def emarsi(conn, cursor, symbol_details, sdf, ema_55, rsi_14, to_date, to_time):
    strategy = 'emarsi'
    select_query = "select direction, position_price from strategy_211 where symbol = '" + symbol_details['symbol'] + "' and date = '" + to_date + "' and strategy = '" + strategy + "';"
    cursor.execute(select_query)
    symbol_date_data = cursor.fetchone()
    if symbol_date_data is not None:
        update_price_in_db(conn, cursor, symbol_date_data, sdf, symbol_details, to_date, strategy)
    else:
        to_timestamp = to_date + " " + to_time
        is_a_signal = False
        last_index = len(sdf.index) - 1
        # logger.info("symbol: " + symbol_details['symbol'] + ", category: " + str(symbol_details['category']) + ", rsi_14_today: " + str(rsi_14_today) + ", ema_55_today: " + str(ema_55_today))
        if rsi_14[last_index] > util.strategy_211_rsi_upper_limit or rsi_14[last_index] < util.strategy_211_rsi_lower_limit:
            is_a_signal = True
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
            insert_signal_in_db_table(conn, cursor, symbol_details, sdf, last_index, strategy, direction, to_date, to_timestamp)


def breakout(conn, cursor, symbol_details, sdf, ema_55, rsi_14, to_date, to_time):
    strategy = 'breakout'
    select_query = "select direction, position_price from strategy_211 where symbol = '" + symbol_details['symbol'] + "' and date = '" + to_date + "' and strategy = '" + strategy + "';"
    cursor.execute(select_query)
    symbol_date_data = cursor.fetchone()
    if symbol_date_data is not None:
        update_price_in_db(conn, cursor, symbol_date_data, sdf, symbol_details, to_date, strategy)
    else:
        direction = 1
        to_timestamp = to_date + " " + to_time
        last_index = len(sdf.index) - 1
        opening_price = sdf['open'][last_index]
        breakout_percentage_diff = opening_price * breakout_percentage / 100
        if sdf['close'][last_index] > (opening_price + breakout_percentage_diff):
            insert_signal_in_db_table(conn, cursor, symbol_details, sdf, last_index, strategy, direction, to_date, to_timestamp)


def smajump(conn, cursor, symbol_details, sdf, sma_44, ema_55, rsi_14, to_date, to_time):
    strategy = 'smajump'
    select_query = "select direction, position_price from strategy_211 where symbol = '" + symbol_details['symbol'] + "' and date = '" + to_date + "' and strategy = '" + strategy + "';"
    cursor.execute(select_query)
    symbol_date_data = cursor.fetchone()
    if symbol_date_data is not None:
        update_price_in_db(conn, cursor, symbol_date_data, sdf, symbol_details, to_date, strategy)
    else:
        direction = 1
        to_timestamp = to_date + " " + to_time
        last_index = len(sdf.index) - 1
        if (
                sdf['close'][last_index - 1] < sdf['open'][last_index - 1] and
                sdf['low'][last_index - 1] < sma_44[last_index - 1] and
                sdf['high'][last_index - 1] > sma_44[last_index - 1]
        ) and (
                sdf['close'][last_index] > sdf['open'][last_index] and
                sdf['low'][last_index] < sma_44[last_index] and
                sdf['close'][last_index] > sma_44[last_index]
        ):
            insert_signal_in_db_table(conn, cursor, symbol_details, sdf, last_index, strategy, direction, to_date, to_timestamp)


def fetch_data_and_scan(kite, symbol_details, from_date, to_date, to_time, interval):
    conn = util.mysql_connection()
    cursor = conn.cursor()
    to_timestamp = to_date + " " + to_time
    records = kite.historical_data(symbol_details['nseToken'], from_date, to_timestamp, interval)
    df = pd.DataFrame(records)
    sdf = StockDataFrame.retype(df)
    sma_44 = sdf['close_44_sma']
    ema_55 = sdf['close_55_ema']
    rsi_14 = sdf['rsi_14']
    emarsi(conn, cursor, symbol_details, sdf, ema_55, rsi_14, to_date, to_time)
    breakout(conn, cursor, symbol_details, sdf, ema_55, rsi_14, to_date, to_time)
    smajump(conn, cursor, symbol_details, sdf, sma_44, ema_55, rsi_14, to_date, to_time)
    conn.close


def create_threads(ids, from_date, to_date, to_time):
    for slot_ids in ids:
        start_id = slot_ids['start']
        end_id = slot_ids['end']
        conn = util.mysql_connection()
        cursor = conn.cursor()
        select_query = "select id, symbol, nseToken, category from equityStocks where nseToken is not NULL and symbol not like '%-BE' and id >= '" + str(
            start_id) + "' and id <= '" + str(end_id) + "';"
        # logger.info("###############################################################################################")
        logger.info("date: " + to_date + ", time: " + to_time + ", select_query: " + select_query)
        cursor.execute(select_query)
        data_analysis_thread_array = []
        for (id, symbol, nseToken, category) in cursor:
            symbol_details = {'id': id, 'symbol': symbol, 'nseToken': nseToken, 'category': category}
            data_analysis_thread = util.ThreadWithReturnValue(target=fetch_data_and_scan, args=(
                kite, symbol_details, from_date, to_date, to_time, 'day'))
            data_analysis_thread.start()
            data_analysis_thread_array.append(data_analysis_thread)
            time.sleep(0.20)

        for data_analysis_thread in data_analysis_thread_array:
            data_analysis_thread.join()


def main(argv):
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

    backtest_dates = []
    backtest_times = []
    # current_timestamp = '2021-07-02 13:00:00'
    current_timestamp = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    to_date = (str(current_timestamp))[0:10]
    to_time = (str(current_timestamp))[11:19]
    backtest_dates.append(to_date)
    backtest_times.append(to_time)

    for backtest_date in backtest_dates:
        for backtest_time in backtest_times:
            to_date = backtest_date
            to_time = backtest_time
            to_date_obj = date(int(to_date[0:4]), int(to_date[5:7]), int(to_date[8:10]))
            from_date = str(datetime.strftime(to_date_obj - timedelta(365 * 3), '%Y-%m-%d'))
            create_threads(ids, from_date, to_date, to_time)


if __name__ == "__main__":
    logger.info("strategy-211-test.py started: " + str(datetime.today().strftime('%Y-%m-%d %H:%M:%S')))
    start_time = time.time()
    main(sys.argv[1:])
    end_time = time.time()
    logger.info("time consumed to run strategy-211-test.py completely: " + str(end_time - start_time))
