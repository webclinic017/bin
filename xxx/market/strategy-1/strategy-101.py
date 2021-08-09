import os
import util
import pandas as pd
from stockstats import StockDataFrame
from datetime import datetime, timedelta
from kiteconnect import KiteConnect


## CREATE table strategy_101_signal(id INT NOT NULL AUTO_INCREMENT, nseToken VARCHAR(255) NOT NULL, category INT NOT NULL, symbol VARCHAR(255) NOT NULL, crossingDay INT NOT NULL, crossingDate VARCHAR(255) NOT NULL, buyingPrice DOUBLE (10, 2) NOT NULL, stoploss DOUBLE (10, 2) NOT NULL, target DOUBLE (10, 2) NOT NULL, sellingDate VARCHAR(255), sellingPrice DOUBLE (10, 2), diff INT, numberOfDays INT, PRIMARY KEY (id));
## select id, category, symbol, crossingDay, crossingDate, buyingPrice, stoploss, target, sellingDate, sellingPrice, diff, numberOfDays from strategy_101_signal;

rsi_upper_limit = 58.5
max_allowed_jump = 5
wait_period_after_ema_crossing = 1
number_of_past_days = 1
buying_price_strategy = -1    # 1 = 'optimistic', 0 = 'average', -1 = 'pessimistic',
run_type = 'back_test'       # 'back_test', 'new_signal',
back_test_new_offset = 13
back_test_old_offset = 34
target_multiplier = 1


def get_target_price_strategy_101(buying_price, stoploss):
    stop_loss_diff = buying_price - stoploss
    target_diff = stop_loss_diff * target_multiplier
    target = buying_price + target_diff
    return target


def save_signal_in_db(sdf, nseToken, category, symbol, crossing_day, today_index):
    print(str(crossing_day) + " category: " + str(category) + ", symbol: " + symbol + ", crossing date: " + str(sdf.index[today_index]))
    conn2 = util.mysql_connection()
    if conn2 is not None:
        cursor2 = conn2.cursor()
        crossingDate = (str(sdf.index[today_index]))[0:10]
        buyingPrice = util.get_buying_price(sdf, today_index, buying_price_strategy)
        stoploss = sdf['low'][today_index + crossing_day]  # adding crossing_day because it is negative
        target = get_target_price_strategy_101(buyingPrice, stoploss)
        selling_price, selling_date, number_of_days = util.get_sell_details(sdf, today_index, buyingPrice, stoploss, target)
        selling_price_str = str(selling_price)
        double_diff = selling_price - buyingPrice
        diff = 0
        if double_diff > 0:
            diff = 1
        elif double_diff < 0:
            diff = -1
        diff_str = str(diff)
        number_of_days_str = str(number_of_days)
        insert_signal_query = "insert into strategy_101_signal (nseToken, category, symbol, crossingDay, crossingDate, buyingPrice, stoploss, target, sellingDate, sellingPrice, diff, numberOfDays) values ('" + nseToken + "', " + str(category) + ", '" + symbol + "', " + str(crossing_day) + ", '" + crossingDate + "', " + str(buyingPrice) + ", " + str(stoploss) + ", " + str(target) + ", '" + selling_date + "', " + selling_price_str + ", " + diff_str + ", " + number_of_days_str + ");"
        # print(insert_signal_query)
        cursor2.execute(insert_signal_query)
        conn2.commit()
        conn2.close


def generate_signal(sdf, today_index, category, symbol, minus_days, nseToken):
    if not util.is_crossing_close_55_ema(sdf, today_index - minus_days):
        return False
    ############################## checks for all jumps after crossing ##############################
    if not util.is_crossing_jump_valid(sdf, today_index - minus_days, today_index, max_allowed_jump):
        return False
    if not util.are_all_green(sdf, today_index - minus_days, today_index):
        return False
    ################# checks if certain attributes are continuously increasing ##################
    max_open_close_array = util.max_array(sdf, ['open', 'close'])
    is_high_increasing = util.is_continuously_increasing(sdf['high'], today_index - minus_days - number_of_past_days, today_index)
    is_candle_increasing = util.is_continuously_increasing(max_open_close_array, today_index - minus_days - number_of_past_days, today_index)
    if not (is_high_increasing or is_candle_increasing):
        return False
    rsi_14_today_index = sdf['rsi_14'][today_index]
    if not sdf['rsi_14'][today_index] > rsi_upper_limit:
        return False
    save_signal_in_db(sdf, nseToken, category, symbol, -1 * minus_days, today_index)
    return True


def check_and_print(sdf, symbol, days, category, nseToken):
    today_index = len(sdf.index) - days
    today_date = str(sdf.index[today_index])
    generated = False
    # if str(sdf.index[today_index]) == '2021-05-03 00:00:00+05:30':
    #     print(str(sdf.index[today_index]))
    if not generated and wait_period_after_ema_crossing >= 0:
        generated = generate_signal(sdf, today_index, category, symbol, 0, nseToken)
    if not generated and wait_period_after_ema_crossing >= 1:
        generated = generate_signal(sdf, today_index, category, symbol, 1, nseToken)
    if not generated and wait_period_after_ema_crossing >= 2:
        generated = generate_signal(sdf, today_index, category, symbol, 2, nseToken)


def method_1(category, interval, lower_range, upper_range):
    cwd = os.getcwd()
    print("cwd: " + cwd)
    api_key = open(cwd + "/../txt/api_key.txt", 'r').read()
    api_secret = open(cwd + "/../txt/api_secret.txt", 'r').read()
    access_token = open(cwd + "/../txt/access_token.txt", 'r').read()

    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)

    from_date = datetime.strftime(datetime.now()-timedelta(365 * 3), '%Y-%m-%d')
    print("from_date: " + from_date)
    to_date = datetime.today().strftime('%Y-%m-%d')
    print("to_date: " + to_date)

    conn1 = util.mysql_connection()
    if conn1 is not None:
        cursor1 = conn1.cursor()
        select_equity_stocks = "select id, symbol, industry, category, nseToken from equityStocks where nseToken is not NULL and category >= '" + str(category) + "';"
        # select_equity_stocks = "select id, symbol, industry, category, nseToken from equityStocks where nseToken is not NULL and category >= '" + str(category) + "' and symbol = 'INDOSTAR';"
        # print("select_equity_stocks: " + select_equity_stocks)
        cursor1.execute(select_equity_stocks)
        for (id, symbol, industry, category, nseToken) in cursor1:
            # print("id: " + str(id) + ", symbol: " + symbol + ", industry: " + industry + ", category: " + str(category) + ", nseToken: " + nseToken)
            records = kite.historical_data(nseToken, from_date=from_date, to_date=to_date, interval=interval)
            df = pd.DataFrame(records)
            # print(df)
            sdf = StockDataFrame.retype(df)
            ema_55 = sdf['close_55_ema']
            rsi_14 = sdf['rsi_14']
            valid_data = []
            sdf_dates = util.get_sdf_dates(sdf)

            # print("$$$$$$$$$$$$$$$$$    " + symbol + "    $$$$$$$$$$$$$$$$$")
            for days in range(lower_range, upper_range):
                check_and_print(sdf, symbol, days, category, nseToken)
            # print("#########################################################")


method_1(1, 'day', 1, 2)
# method_1(1, 'day', 15, 75)
