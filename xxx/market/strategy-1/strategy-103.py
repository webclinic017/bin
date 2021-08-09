import os
import util
import pandas as pd
from stockstats import StockDataFrame
from datetime import datetime, timedelta
from kiteconnect import KiteConnect


rsi_upper_limit = 60
max_allowed_jump = 5


def is_crossing_jump_valid(today_minus_0):
    open_price = today_minus_0['open']
    close_price = today_minus_0['close']
    jump = close_price - open_price
    percentage_jump = (jump * 100) / close_price
    if percentage_jump < 5:
        return True
    else:
        return False


def is_crossing_close_55_ema(today_minus_0):
    if today_minus_0['low'] < today_minus_0['close_55_ema'] < today_minus_0['high']:
        return True
    else:
        return False


def is_green(today_minus_0):
    if today_minus_0['open'] < today_minus_0['close']:
        return True
    else:
        return False

    
def check_and_print(symbol, valid_data, days, category):
    i = len(valid_data) - days
    current_minus_four = valid_data[i - 4]
    current_minus_three = valid_data[i - 3]
    current_minus_two = valid_data[i - 2]
    current_minus_one = valid_data[i - 1]
    current_date_data = valid_data[i]
    generated = False

    # price crossed today, continuous increasing, rsi crossed today
    if not generated and current_date_data['low'] < current_date_data['close_55_ema'] < current_date_data['high']:
        if current_date_data['open'] < current_date_data['close']:
            if current_minus_two['high'] < current_minus_one['high'] < current_date_data['high']:
                if current_date_data['rsi_14'] > rsi_upper_limit:
                    # print(current_minus_four)
                    # print(current_minus_three)
                    # print(current_minus_two)
                    # print(current_minus_one)
                    # print(current_date_data)
                    toPrint = "aaaa category: " + str(category) + ", symbol: " + symbol + ", crossing date: " + current_date_data['date']
                    check_jump(toPrint, current_date_data)
                    generated = True

    # price crossed yesterday, continuous increasing, continuously green, rsi crossed today
    if not generated and current_minus_one['low'] < current_minus_one['close_55_ema'] < current_minus_one['high']:
        if current_minus_one['open'] < current_minus_one['close'] and current_date_data['open'] < current_date_data['close']:
            if current_minus_three['high'] < current_minus_two['high'] < current_minus_one['high'] < current_date_data['high']:
                if current_date_data['rsi_14'] > rsi_upper_limit:
                    # print(current_minus_four)
                    # print(current_minus_three)
                    # print(current_minus_two)
                    # print(current_minus_one)
                    # print(current_date_data)
                    toPrint = "bbbb category: " + str(category) + ", symbol: " + symbol + ", crossing date: " + current_minus_one['date']
                    check_jump(toPrint, current_minus_one)
                    generated = True

    # price crossed day before yesterday, continuous increasing, continuously green, rsi crossed today
    if not generated and current_minus_one['low'] < current_minus_one['close_55_ema'] < current_minus_one['high']:
        if current_minus_two['open'] < current_minus_two['close'] and current_minus_one['open'] < current_minus_one['close'] and current_date_data['open'] < current_date_data['close']:
            if current_minus_four['high'] < current_minus_three['high'] < current_minus_two['high'] < current_minus_one['high'] < current_date_data['high']:
                if current_date_data['rsi_14'] > rsi_upper_limit:
                    # print(current_minus_four)
                    # print(current_minus_three)
                    # print(current_minus_two)
                    # print(current_minus_one)
                    # print(current_date_data)
                    toPrint = "cccc category: " + str(category) + ", symbol: " + symbol + ", crossing date: " + current_minus_two['date']
                    check_jump(toPrint, current_minus_two)
                    generated = True


def method_1(category, interval, lower_range, upper_range):
    cwd = os.getcwd()
    print("cwd: " + cwd)
    api_key = open(cwd + "/../txt/api_key.txt", 'r').read()
    api_secret = open(cwd + "/../txt/api_secret.txt", 'r').read()
    access_token = open(cwd + "/../txt/access_token.txt", 'r').read()

    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)

    from_date = datetime.strftime(datetime.now()-timedelta(365 * 2), '%Y-%m-%d')
    print("from_date: " + from_date)
    to_date = datetime.today().strftime('%Y-%m-%d')
    print("to_date: " + to_date)

    conn1 = util.mysql_connection()
    if conn1 is not None:
        cursor1 = conn1.cursor()
        select_equity_stocks = "select id, symbol, industry, category, nseToken from equityStocks where nseToken is not NULL and isBlacklisted = 0 and category >= '" + str(category) + "';"
        # select_equity_stocks = "select id, symbol, industry, category, nseToken from equityStocks where nseToken is not NULL and isBlacklisted = 0 and category >= '" + str(category) + "' and symbol = 'INFIBEAM';"
        # print("select_equity_stocks: " + select_equity_stocks)
        cursor1.execute(select_equity_stocks)
        for (id, symbol, industry, category, nseToken) in cursor1:
            # print("id: " + str(id) + ", symbol: " + symbol + ", industry: " + industry + ", category: " + str(category) + ", nseToken: " + nseToken)
            records = kite.historical_data(nseToken, from_date=from_date, to_date=to_date, interval=interval)
            df = pd.DataFrame(records)
            sdf = StockDataFrame.retype(df)
            # print(sdf)
            ema_55 = sdf['close_55_ema']
            rsi_14 = sdf['rsi_14']
            valid_data = []
            counter = 0
            for row in sdf.iterrows():
                date = row[0]
                date_open = row[1][0]
                date_high = row[1][1]
                date_low = row[1][2]
                date_close = row[1][3]
                date_volume = row[1][4]
                date_close_55_ema = row[1][5]
                date_rsi_14 = row[1][9]
                key_date = str(date)
                key_date = key_date[0:10]
                date_data = {"date": key_date, "open": date_open, "high": date_high, "low": date_low, "close": date_close,
                             "volume": date_volume, "close_55_ema": date_close_55_ema, "rsi_14": date_rsi_14}
                valid_data.append(date_data)
                counter = counter + 1

            # print("$$$$$$$$$$$$$$$$$    " + symbol + "    $$$$$$$$$$$$$$$$$")
            # check_and_print(symbol, valid_data, 1, category)

            # print("$$$$$$$$$$$$$$$$$    " + symbol + "    $$$$$$$$$$$$$$$$$")
            for days in range(lower_range, upper_range):
                check_and_print(symbol, valid_data, days, category)
            # print("#########################################################")


# method_1(1, 'day', 1, 2)
method_1(1, 'day', 11, 32)
