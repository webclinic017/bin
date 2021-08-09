import sys
import util
import time
import getopt
import logging
import pandas as pd
from kiteconnect import KiteConnect
from stockstats import StockDataFrame
from datetime import date, datetime, timedelta


interval_val = 3
volume_multiplier = 0.02    # can't be greater than 0.05
max_money_in_one_stock = 15000
max_vol_for_testing = 1
order_executed_check_interval = 2
max_checks_before_cancellation = 4
volatility_multiplier = 0.8    # can't be less than 0.1


logger = util.get_logger(util.baby_0_dir + 'txt/strategy-201-red.log')


def get_modulus_timestamp(current_timestamp_str):
    global interval_val
    hour_val = int(current_timestamp_str[11:13])
    minute_val = int(current_timestamp_str[14:16])
    second_val = int(current_timestamp_str[17:19])
    if minute_val == 0 or (minute_val == 1 and second_val <= 30):
        hour_val = hour_val - 1
        minute_val = 59
        second_val = 59
    elif minute_val % interval_val == 0:
        minute_val = minute_val - 1
        second_val = 59
    elif minute_val % interval_val == 1 and second_val <= 30:
        minute_val = minute_val - 2
        second_val = 59
    elif (minute_val % interval_val == 1 and second_val >= 31):
        minute_val = minute_val + 1
        second_val = 59
    elif minute_val % interval_val == 2:
        second_val = 59
    hour_val_str = str(hour_val)
    minute_val_str = str(minute_val)
    second_val_str = str(second_val)
    if len(hour_val_str) == 1:
        hour_val_str = "0" + hour_val_str
    if len(minute_val_str) == 1:
        minute_val_str = "0" + minute_val_str
    modulus_timestamp_str = hour_val_str + ":" + minute_val_str + ":" + second_val_str
    return modulus_timestamp_str


def check_volatility(kite, symbol, confirmation_close, confirmation_high):
    is_volatile = True
    confirmation_high_close_avg = (confirmation_high + confirmation_close) / 2
    diff_high_close_avg_close = confirmation_high_close_avg - confirmation_close
    normalized_diff_high_close_avg_close = diff_high_close_avg_close * volatility_multiplier
    normalized_confirmation_high_close_avg = confirmation_close + normalized_diff_high_close_avg_close
    normalized_min_allowed_low_price = confirmation_close - normalized_diff_high_close_avg_close
    ltp = kite.ltp('NSE:' + symbol)
    last_traded_price = ltp['NSE:' + symbol]['last_price']
    if normalized_confirmation_high_close_avg > last_traded_price > normalized_min_allowed_low_price:
        is_volatile = False
    return is_volatile


def check_lower_wick(confirmation_open, confirmation_close, confirmation_high, confirmation_low):
    lower_wick_too_long = False
    lower_wick = confirmation_close - confirmation_low
    body = confirmation_open - confirmation_close
    if lower_wick > body:
        lower_wick_too_long = True
    return lower_wick_too_long


def place_position_order(kite, symbol, volume, confirmation_open, confirmation_close, confirmation_high, confirmation_low):
    global volatility_multiplier
    global max_vol_for_testing

    # volume = max_vol_for_testing

    blocked = 0
    order_id_str = ''
    is_volatile = check_volatility(kite, symbol, confirmation_close, confirmation_high)
    if is_volatile:
        blocked = 2
    is_lower_wick_too_long = check_lower_wick(confirmation_open, confirmation_close, confirmation_high, confirmation_low)
    if is_lower_wick_too_long:
        blocked = 3
    if blocked == 0:
        try:
            order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                        exchange=kite.EXCHANGE_NSE,
                                        tradingsymbol=symbol,
                                        transaction_type=kite.TRANSACTION_TYPE_SELL,
                                        quantity=volume,
                                        product=kite.PRODUCT_MIS,
                                        order_type=kite.ORDER_TYPE_MARKET,
                                        # price=price,
                                        validity='DAY'
                                        )
            order_id_str = str(order_id)
            logger.info("order_id: " + str(order_id))
        except Exception as e:
            logger.info("exception in placing order for the symbol: " + symbol + ", " + str(e))
            blocked = 1
    return blocked, order_id_str


def place_target_order(kite, symbol, price, volume):
    order_id_str = ''
    try:
        order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                    exchange=kite.EXCHANGE_NSE,
                                    tradingsymbol=symbol,
                                    transaction_type=kite.TRANSACTION_TYPE_BUY,
                                    quantity=volume,
                                    product=kite.PRODUCT_MIS,
                                    order_type=kite.ORDER_TYPE_LIMIT,
                                    price=price,
                                    validity='DAY'
                                    )
        order_id_str = str(order_id)
        logger.info("order_id: " + str(order_id))
    except Exception as e:
        logger.info("exception in placing order for the symbol: " + symbol + ", " + str(e))
        order_id_str = 'exception'
    return order_id_str


def get_position_price(kite, position_order_id):
    position_price = -1
    total_quantified_price = 0
    total_quantity = 0
    trades = kite.order_trades(position_order_id)
    for trade in trades:
        this_quantity = trade['quantity']
        this_price = trade['average_price']
        this_quantified_price = this_quantity * this_price
        total_quantified_price += this_quantified_price
        total_quantity += this_quantity
    position_price = total_quantified_price / total_quantity
    position_price = round(position_price, 2)
    return position_price, total_quantity


def check_confirmation(kite, symbol_details, interval, today_date_str, back_day_scan_start_timestamp, modulus_timestamp):
    global volume_multiplier
    global max_money_in_one_stock
    global max_vol_for_testing
    records = kite.historical_data(symbol_details['nseToken'], back_day_scan_start_timestamp, modulus_timestamp, interval)
    df = pd.DataFrame(records)
    sdf = StockDataFrame.retype(df)
    rsi_14 = sdf['rsi_14']
    confirmation_index = -1
    position_price = -1
    position_volume = -1
    stoploss = -1
    target = -1
    signal_timestamp_index = -1
    for i in range(len(sdf.index) - 1, -1, -1):
        if (str(sdf.index[i]))[0:19] == symbol_details['signal_timestamp']:
            signal_timestamp_index = i
            break
    logger.info("symbol: " + symbol_details['symbol'] + ", ---- signal_timestamp_index ---- rsi_14: " + str(rsi_14[signal_timestamp_index]) + ", volume: " + str(sdf['volume'][signal_timestamp_index]))
    if rsi_14[signal_timestamp_index] > util.strategy_201_red_signal_limit and sdf['volume'][signal_timestamp_index] > (3 * util.strategy_201_red_min_per_minute_trade):
        for i in range(signal_timestamp_index, len(sdf.index)):
            if sdf['open'][i] > sdf['close'][i]:
                confirmation_index = i
                break
    if confirmation_index != -1:
        position_volume = int(sdf['volume'][confirmation_index] * volume_multiplier)
        confirmation_open = sdf['open'][confirmation_index]
        confirmation_high = sdf['high'][confirmation_index]
        confirmation_low = sdf['low'][confirmation_index]
        confirmation_close = sdf['close'][confirmation_index]
        confirmation_volume = sdf['volume'][confirmation_index]
        logger.info("symbol: " + symbol_details['symbol'] + ", confirmation => timestamp: " + str(sdf.index[confirmation_index]) + ", open: " + str(confirmation_open) + ", close: " + str(confirmation_close) + ", low: " + str(confirmation_low) + ", high: " + str(confirmation_high) + ", volume: " + str(confirmation_volume))
        max_allowed_vol = int(max_money_in_one_stock / confirmation_close)
        logger.info("symbol: " + symbol_details['symbol'] + ", max_money_in_one_stock: " + str(max_money_in_one_stock) + ", position_volume: " + str(position_volume) + ", max_allowed_vol: " + str(max_allowed_vol))
        if position_volume > max_allowed_vol:
            position_volume = max_allowed_vol
        conn = util.mysql_connection()
        cursor = conn.cursor()
        is_blocked, position_order_id = place_position_order(kite, symbol_details['symbol'], position_volume, confirmation_open, confirmation_close, confirmation_high, confirmation_low)
        logger.info("symbol: " + symbol_details['symbol'] + ", is_blocked: " + str(is_blocked) + ", position_order_id: " + position_order_id)
        if is_blocked == 0:
            update_query = "update equityStocks_" + today_date_str + " set position_order_id = '" + position_order_id + "' where symbol = '" + str(symbol_details['symbol']) + "';"
            cursor.execute(update_query)
            conn.commit()

            position_price, position_volume = get_position_price(kite, position_order_id)
            logger.info("symbol: " + symbol_details['symbol'] + ", position_price: " + str(position_price) + ", position_volume: " + str(position_volume))
            if position_price != -1:
                stoploss = sdf['high'][confirmation_index]
                stoploss_per_stock = position_price - stoploss
                stoploss_amount = stoploss_per_stock * position_volume
                target = position_price - (sdf['high'][confirmation_index] - position_price)
                target_per_stock = position_price - target
                target_amount = target_per_stock * position_volume
                logger.info("symbol: " + symbol_details['symbol'] + ", stoploss: " + str(stoploss) + ", target: " + str(target))
                update_query = "update equityStocks_" + today_date_str + " set confirmation_timestamp = '" + (str(
                    sdf.index[confirmation_index]))[0:19] + "', position_price = '" + str(
                    position_price) + "', position_volume = '" + str(position_volume) + "', stoploss = '" + str(
                    stoploss) + "', target = '" + str(target) + "', stoploss_amount = '" + str(
                    stoploss_amount) + "', target_amount = '" + str(target_amount) + "' where symbol = '" + str(symbol_details['symbol']) + "';"
                logger.info("symbol: " + symbol_details['symbol'] + ", update_query: " + update_query)
                cursor.execute(update_query)
                conn.commit()

                logger.info("symbol: " + symbol_details['symbol'] + ", target: " + str(target) + ", position_volume: " + str(position_volume))
                target_order_id = place_target_order(kite, symbol_details['symbol'], target, position_volume)
                logger.info("symbol: " + symbol_details['symbol'] + ", target_order_id: " + target_order_id)
                update_query = "update equityStocks_" + today_date_str + " set target_order_id = '" + target_order_id + "' where symbol = '" + str(symbol_details['symbol']) + "';"
                logger.info("symbol: " + symbol_details['symbol'] + ", update_query: " + update_query)
                cursor.execute(update_query)
                conn.commit()
        else:
            logger.info("symbol: " + symbol_details['symbol'] + ", going to save blocked status in db.")
            update_query = "update equityStocks_" + today_date_str + " set is_blocked = '" + is_blocked + "' where symbol = '" + str(symbol_details['symbol']) + "';"
            cursor.execute(update_query)
            conn.commit()
        conn.close


def main(argv):
    global interval_val
    interval = str(interval_val) + 'minute'
    conn = util.mysql_connection()
    cursor = conn.cursor()
    # today_date = "2021-06-24"
    today_date = datetime.today().strftime('%Y-%m-%d')
    date_vals = str(today_date).split('-')
    today_date_str = date_vals[0] + "_" + date_vals[1] + "_" + date_vals[2]

    kite = util.get_kite()

    select_query = "select id, symbol, nseToken, signal_timestamp from equityStocks_" + today_date_str + " where signal_timestamp is not NULL and is_blocked = 0 and confirmation_timestamp is NULL;"
    cursor.execute(select_query)
    # current_timestamp_str = "2021-06-24 09:17:55"
    current_timestamp = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    current_timestamp_str = str(current_timestamp)
    modulus_timestamp_str = str(today_date) + " " + get_modulus_timestamp(current_timestamp_str)
    logger.info("modulus_timestamp_str: " + modulus_timestamp_str)

    back_day_scan_start_timestamp = util.get_back_day_scan_start_timestamp(kite, util.strategy_201_red_timedelta_days)

    data_analysis_thread_array = []
    for (id, symbol, nseToken, signal_timestamp) in cursor:
        symbol_details = {'id': id, 'symbol': symbol, 'nseToken': nseToken, 'signal_timestamp': signal_timestamp}
        # check_confirmation(kite, symbol_details, interval, today_date_str, modulus_timestamp_str)
        data_analysis_thread = util.ThreadWithReturnValue(target=check_confirmation, args=(kite, symbol_details, interval, today_date_str, back_day_scan_start_timestamp, modulus_timestamp_str))
        data_analysis_thread.start()
        data_analysis_thread_array.append(data_analysis_thread)
        time.sleep(0.15)

    for data_analysis_thread in data_analysis_thread_array:
        data_analysis_thread.join()

    # for i in range(0, max_checks_before_cancellation):
    #     time.sleep(order_executed_check_interval)


if __name__ == "__main__":
    time.sleep(54)
    logger.info("strategy-201-red-confirmation.py started after sleep: " + str(datetime.today().strftime('%Y-%m-%d %H:%M:%S')))
    start_time = time.time()
    main(sys.argv[1:])
    end_time = time.time()
    logger.info("time consumed to run completely: " + str(end_time - start_time))
