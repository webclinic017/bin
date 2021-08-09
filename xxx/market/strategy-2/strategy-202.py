import os
import util
import pandas as pd
from stockstats import StockDataFrame
from datetime import datetime, timedelta
from kiteconnect import KiteConnect


def check_rsi_and_print(sdf, symbol, days, category, nseToken):
    today_index = len(sdf.index) - days
    today_date = str(sdf.index[today_index])
    rsi_14 = sdf['rsi_14'][today_index]
    # print("symbol: " + symbol + ", days: " + str(days) + ", timestamp: " + today_date + ", rsi_14: " + str(rsi_14))
    if rsi_14 < 60:
        print("category: " + str(category) + ", symbol: " + symbol + ", timestamp: " + today_date + ", rsi_14: " + str(rsi_14))
        return True


def method_1(category, interval, day):
    upper_range = (day * 75) + 1
    print("upper_range: " + str(upper_range))
    lower_range = upper_range - 7
    print("lower_range: " + str(lower_range))
    api_key = open(util.baby_0_dir + "txt/api_key.txt", 'r').read()
    api_secret = open(util.baby_0_dir + "txt/api_secret.txt", 'r').read()
    access_token = open(util.baby_0_dir + "txt/access_token.txt", 'r').read()

    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)

    from_date = datetime.strftime(datetime.now()-timedelta(12), '%Y-%m-%d %H:%M:00')
    print("from_date: " + from_date)
    to_date = datetime.today().strftime('%Y-%m-%d %H:%M:00')
    print("to_date: " + to_date)

    conn1 = util.mysql_connection()
    if conn1 is not None:
        cursor1 = conn1.cursor()
        select_equity_stocks = "select id, symbol, industry, category, nseToken from equityStocks where nseToken is not NULL and category >= '" + str(category) + "';"
        # select_equity_stocks = "select id, symbol, industry, category, nseToken from equityStocks where nseToken is not NULL and symbol = 'ADANIPORTS';"
        cursor1.execute(select_equity_stocks)
        for (id, symbol, industry, category, nseToken) in cursor1:
            # print("id: " + str(id) + ", symbol: " + symbol + ", industry: " + industry + ", category: " + str(category) + ", nseToken: " + nseToken)
            records = kite.historical_data(nseToken, from_date=from_date, to_date=to_date, interval=interval)
            df = pd.DataFrame(records)
            # print(df)
            sdf = StockDataFrame.retype(df)
            sma_44 = sdf['close_44_sma']
            ema_55 = sdf['close_55_ema']
            rsi_14 = sdf['rsi_14']
            valid_data = []
            sdf_dates = util.get_sdf_dates(sdf)

            today_index = len(sdf.index) - upper_range + 1
            if sdf['rsi_14'][today_index] > 70:
                print("category: " + str(category) + ", symbol: " + symbol + ", rsi_14: " + str(sdf['rsi_14'][today_index]))
                # for days in range(upper_range - 1, lower_range - 1, -1):
                #     is_rsi_above_limit = check_rsi_and_print(sdf, symbol, days, category, nseToken)
                #     if is_rsi_above_limit:
                #         break


# method_1(5, '5minute', 1, 76)
# method_1(5, '5minute', 76, 151)
# method_1(5, '5minute', 151, 226)
# method_1(5, '5minute', 226, 300)
method_1(1, '5minute', 1)
