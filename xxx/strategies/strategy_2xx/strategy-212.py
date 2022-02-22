import sys
import util
import time
import getopt
import logging
import pandas as pd
from kiteconnect import KiteConnect
from stockstats import StockDataFrame
from datetime import date, datetime, timedelta


logger = util.get_logger(util.baby_0_dir + 'txt/strategy-211.log')
kite = util.get_kite()


def place_position_order(kite, symbol, volume_val, open_price, close_price, high_price, low_price, avg_vol_per_min):
    logger.info("symbol: " + symbol + ", close_price: " + str(close_price) + ", avg_vol_per_min: " + str(avg_vol_per_min) + ", volume_val: " + str(volume_val))
    is_blocked = 0
    position_volume = 0
    if close_price > util.stock_max_allowed_price:
        is_blocked = 1
    if is_blocked == 0:
        if avg_vol_per_min > util.strategy_212_min_per_minute_trade:
            avg_amount_per_min = avg_vol_per_min * close_price
            logger.info("symbol: " + symbol + ", avg_amount_per_min: " + str(avg_amount_per_min))
            if avg_amount_per_min > util.strategy_212_max_amount_allowed_in_one_stock:
                position_volume = int(util.strategy_212_max_amount_allowed_in_one_stock / close_price)
            else:
                position_volume = avg_vol_per_min
            if position_volume > volume_val:
                position_volume = volume_val
        if position_volume == 0:
            is_blocked = 2
    logger.info("symbol: " + symbol + ", is_blocked: " + str(is_blocked) + ", volume: " + str(position_volume))
    order_id_str = ''
    if is_blocked == 0:
        try:
            order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                        exchange=kite.EXCHANGE_NSE,
                                        tradingsymbol=symbol,
                                        transaction_type=kite.TRANSACTION_TYPE_SELL,
                                        quantity=position_volume,
                                        product=kite.PRODUCT_MIS,
                                        order_type=kite.ORDER_TYPE_MARKET,
                                        # price=price,
                                        validity='DAY'
                                        )
            order_id_str = str(order_id)
            logger.info("order_id: " + str(order_id))
        except Exception as e:
            logger.info("exception in placing order for the symbol: " + symbol + ", " + str(e))
            blocked = 3
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


def main(argv):
    current_timestamp = str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    today_date = current_timestamp[0:10]
    yesterday_date = util.get_strategy_211_yesterday_date(kite, today_date)
    conn_select = util.mysql_connection()
    cursor_select = conn_select.cursor()
    conn = util.mysql_connection()
    cursor = conn.cursor()
    select_query = "select symbol, nseToken, avg_vol_per_min from strategy_211 where date = '" + yesterday_date + "' and strategy = 'emarsi' and direction = '-1' and is_blocked = '0' and will_emarsi_decrease_tomorrow = '1' and position_order_id is NULL;"
    print("select_query: " + select_query)
    cursor_select.execute(select_query)
    for (symbol, nseToken, avg_vol_per_min) in cursor_select:
        today_start_timestamp = today_date + " " + "09:15:00"
        records = kite.historical_data(nseToken, today_start_timestamp, current_timestamp, 'minute')
        df = pd.DataFrame(records)
        sdf = StockDataFrame.retype(df)
        second_last_index = len(sdf.index) - 2
        open_price = sdf['open'][second_last_index]
        high_price = sdf['high'][second_last_index]
        low_price = sdf['low'][second_last_index]
        close_price = sdf['close'][second_last_index]
        volume_val = sdf['volume'][second_last_index]
        logger.info("symbol: " + symbol + ", timestamp: " + str(sdf.index[second_last_index]) + ", open_price: " + str(open_price) + ", high_price: " + str(high_price) + ", low_price: " + str(low_price) + ", close_price: " + str(close_price) + ", volume_val: " + str(volume_val))
        if open_price > close_price and (close_price - low_price) < (open_price - close_price):
            is_blocked, position_order_id = place_position_order(kite, symbol, volume_val, open_price, close_price, high_price, low_price, avg_vol_per_min)
            logger.info("symbol: " + symbol + ", is_blocked: " + str(is_blocked) + ", position_order_id: " + position_order_id)
            if is_blocked == 0:
                update_query = "update strategy_211 set position_order_id = '" + position_order_id + "' where symbol = '" + symbol + "' and date = '" + yesterday_date + "' and strategy = 'emarsi';"
                logger.info("update_query: " + update_query)
                cursor.execute(update_query)
                conn.commit()

                position_price, position_volume = get_position_price(kite, position_order_id)
                logger.info("symbol: " + symbol + ", position_price: " + str(position_price) + ", position_volume: " + str(position_volume))
                if position_price != -1:
                    target_price = position_price - ((position_price * util.strategy_212_target_percentage) / 100)
                    target_price = round(target_price, 1)
                    logger.info("symbol: " + symbol + ", target: " + str(target_price))
                    update_query = "update strategy_211 set position_price = '" + str(position_price) + "', position_volume = '" + str(position_volume) + "', target_price = '" + str(target_price) + "' where symbol = '" + symbol + "' and date = '" + yesterday_date + "' and strategy = 'emarsi';"
                    logger.info("symbol: " + symbol + ", update_query: " + update_query)
                    cursor.execute(update_query)
                    conn.commit()

                    logger.info("symbol: " + symbol + ", target: " + str(target_price) + ", position_volume: " + str(position_volume))
                    target_order_id = place_target_order(kite, symbol, target_price, position_volume)
                    logger.info("symbol: " + symbol + ", target_order_id: " + target_order_id)
                    update_query = "update strategy_211 set target_order_id = '" + target_order_id + "' where symbol = '" + symbol + "' and date = '" + yesterday_date + "' and strategy = 'emarsi';"
                    logger.info("symbol: " + symbol + ", update_query: " + update_query)
                    cursor.execute(update_query)
                    conn.commit()
            else:
                logger.info("symbol: " + symbol + ", going to save blocked status in db.")
                update_query = "update strategy_211 set is_blocked = '" + is_blocked + "' where symbol = '" + symbol + "' and date = '" + yesterday_date + "' and strategy = 'emarsi';"
                cursor.execute(update_query)
                conn.commit()
    conn.close
    conn_select.close


if __name__ == "__main__":
    time.sleep(3)
    logger.info("strategy-212.py started after sleep.")
    start_time = time.time()
    main(sys.argv[1:])
    end_time = time.time()
    logger.info("time consumed to run strategy-212.py completely: " + str(end_time - start_time))
