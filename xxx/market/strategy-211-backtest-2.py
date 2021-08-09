import sys
import util
import time
import copy
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
stoploss_percentage = 0.5
stoploss_jump_percentage = 0.1


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


def main(argv):
    conn = util.mysql_connection()
    cursor = conn.cursor()
    conn1 = util.mysql_connection()
    cursor1 = conn1.cursor()
    select_query = "select symbol, nseToken from equityStocks where nseToken is not NULL;"
    cursor.execute(select_query)
    symbol_nseToken = {}
    for (symbol, nseToken) in cursor:
        symbol_nseToken[symbol] = nseToken
    # select_query = "select date, symbol, category, confirmation_timestamp from strategy_211_backtest_1 where date = '2021-06-07' and symbol = 'YESBANK';"
    select_query = "select date, symbol, category, confirmation_timestamp from strategy_211_backtest_1;"
    cursor.execute(select_query)
    for (this_date, symbol, category, confirmation_timestamp) in cursor:
        yesterday_date = util.get_strategy_211_yesterday_date(kite, this_date)
        yesterday_date_obj = date(int(yesterday_date[0:4]), int(yesterday_date[5:7]), int(yesterday_date[8:10]))
        from_date = str(datetime.strftime(yesterday_date_obj - timedelta(365 * 3), '%Y-%m-%d'))
        historical_records = kite.historical_data(symbol_nseToken[symbol], from_date, yesterday_date, 'day')
        historical_df = pd.DataFrame(historical_records)
        df_size = len(historical_df.index)
        this_start_timestamp = this_date + " " + "00:00:00"
        today_confirmation_records = kite.historical_data(symbol_nseToken[symbol], this_start_timestamp, confirmation_timestamp, '5minute')
        today_confirmation_df = pd.DataFrame(today_confirmation_records)
        today_timestamp = pd.Timestamp(tz=gettz('Asia/Kolkata'), year=int(this_date[0:4]), month=int(this_date[5:7]), day=int(this_date[8:10]), hour=0, minute=0, second=0)
        current_timestamp = ""
        today_open = today_confirmation_df['open'][0]
        today_high = -20000000
        today_low = 20000000
        today_close = -1
        today_volume = 0
        today_ema = -1
        today_rsi = -1
        current_index = -1
        for i in range(0, len(today_confirmation_df.index) - 1):
            current_index = i
            df = copy.deepcopy(historical_df)
            current_timestamp = (str(today_confirmation_df['date'][i]))[0:19]
            today_close = today_confirmation_df['close'][i]
            if today_high < today_confirmation_df['high'][i]:
                today_high = today_confirmation_df['high'][i]
            if today_low > today_confirmation_df['low'][i]:
                today_low = today_confirmation_df['low'][i]
            today_volume += today_confirmation_df['volume'][i]
            df.loc[df_size] = [today_timestamp, today_open, today_high, today_low, today_close, today_volume]
            sdf = StockDataFrame.retype(df)
            ema_55 = sdf['close_55_ema']
            rsi_14 = sdf['rsi_14']
            today_ema = ema_55[df_size]
            today_rsi = rsi_14[df_size]
            # print("timestamp: " + current_timestamp + ", open: " + str(today_open) + ", high: " + str(today_high) + ", low: " + str(today_low) + ", close: " + str(today_close) + ", volume: " + str(today_volume) + ", ema: " + str(ema_55[df_size]) + ", rsi: " + str(rsi_14[df_size]))

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
                position_volume = 0
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
                insert_query = "insert into strategy_211_backtest_2(date, symbol, category, nseToken, is_blocked, direction, confirmation_timestamp, avg_vol_per_min, position_price, position_volume, till_now_high, till_now_low) values ('" + this_date + "', '" + symbol + "', '" + str(category) + "', '" + str(
                    symbol_nseToken[symbol]) + "', '" + str(is_blocked) + "', '" + str(
                    direction) + "', '" + current_timestamp + "', '" + str(avg_vol_per_min) + "', '" + str(
                    position_price) + "', '" + str(position_volume) + "', '" + str(till_now_high) + "', '" + str(
                    till_now_low) + "');"
                logger.info("insert_query: " + insert_query)
                cursor1.execute(insert_query)
                conn1.commit()
                break
        next_timestamp = (str(today_confirmation_df['date'][current_index + 1]))[0:19]
        update_remaining_day_high_low(this_date, symbol, next_timestamp)
        # break
    conn1.close
    conn.close


def check_blocked(date, symbol, category, nseToken, is_blocked, direction, confirmation_timestamp, avg_vol_per_min, position_price, position_volume):
    blocked = 0
    if is_blocked != 0:
        blocked = is_blocked
    return blocked


def update_remaining_day_high_low(this_date, this_symbol, next_timestamp):
    conn = util.mysql_connection()
    cursor = conn.cursor()
    conn1 = util.mysql_connection()
    cursor1 = conn1.cursor()
    select_to_date_query = "select date, symbol, category, nseToken, is_blocked, direction, confirmation_timestamp, avg_vol_per_min, position_price, position_volume, till_now_high, till_now_low from strategy_211_backtest_2 where date = '" + this_date + "' and symbol = '" + this_symbol + "';"
    cursor.execute(select_to_date_query)
    for (date, symbol, category, nseToken, is_blocked, direction, confirmation_timestamp, avg_vol_per_min, position_price, position_volume, till_now_high, till_now_low) in cursor:
        is_blocked = check_blocked(date, symbol, category, nseToken, is_blocked, direction, confirmation_timestamp, avg_vol_per_min, position_price, position_volume)
        if is_blocked != 0:
            update_query = "update strategy_211_backtest_2 set is_blocked = '" + str(is_blocked) + "' where date = '" + date + "' and symbol = '" + symbol + "';"
            logger.info("update_query: " + update_query)
            cursor1.execute(update_query)
            conn1.commit()
        else:
            stoploss_price = -1
            stoploss_percentage_diff = (position_price * stoploss_percentage) / 100
            stoploss_jump_percentage_diff = (position_price * stoploss_jump_percentage) / 100
            if direction == 1:
                stoploss_price = position_price - stoploss_percentage_diff
            else:
                stoploss_price = position_price + stoploss_percentage_diff
            # start_time = confirmation_timestamp
            start_time = next_timestamp
            end_time = date + " " + "15:29:59"
            records = kite.historical_data(nseToken, start_time, end_time, 'minute')
            df = pd.DataFrame(records)
            sdf = StockDataFrame.retype(df)
            # logger.info(sdf)
            exit_price = -1
            exit_timestamp = ""
            moving_position_price = position_price
            for i in range(0, len(sdf.index)):
                if direction == 1:
                    if sdf['low'][i] < stoploss_price:
                        exit_price = stoploss_price
                        exit_timestamp = (str(sdf.index[i]))[0:19]
                        break
                    else:
                        if sdf['high'][i] > (moving_position_price + stoploss_jump_percentage_diff):
                            moving_position_price = sdf['high'][i] - stoploss_jump_percentage_diff
                            stoploss_price = moving_position_price - stoploss_percentage_diff
                if direction == -1:
                    if sdf['high'][i] > stoploss_price:
                        exit_price = stoploss_price
                        exit_timestamp = (str(sdf.index[i]))[0:19]
                        break
                    else:
                        if sdf['low'][i] < (moving_position_price - stoploss_jump_percentage_diff):
                            moving_position_price = sdf['low'][i] + stoploss_jump_percentage_diff
                            stoploss_price = moving_position_price + stoploss_percentage_diff
            if exit_price == -1:
                exit_price = sdf['close'][len(sdf.index) - 1]
                exit_timestamp = (str(sdf.index[len(sdf.index) - 1]))[0:19]
            profit_loss_per_share = 0
            if direction == 1:
                profit_loss_per_share = exit_price - position_price
            elif direction == -1:
                profit_loss_per_share = position_price - exit_price
            percentage_profit_loss_per_share = (profit_loss_per_share * 100) / position_price
            total_profit_loss = profit_loss_per_share * position_volume
            update_query = "update strategy_211_backtest_2 set exit_price = '" + str(exit_price) + "', exit_timestamp = '" + exit_timestamp + "', profit_loss_per_share = '" + str(profit_loss_per_share) + "', percentage_profit_loss_per_share = '" + str(percentage_profit_loss_per_share) + "', total_profit_loss = '" + str(total_profit_loss) + "' where date = '" + date + "' and symbol = '" + symbol + "';"
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
