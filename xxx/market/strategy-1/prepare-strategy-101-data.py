import os
import util
import pandas as pd
from stockstats import StockDataFrame
from datetime import datetime, timedelta
from kiteconnect import KiteConnect


def prepare_data(stock_symbol):
    conn1 = util.mysql_connection()
    conn2 = util.mysql_connection()
    if conn1 is not None:
        cursor1 = conn1.cursor()
        cursor2 = conn2.cursor()
        select_symbol_from_day_data = "select * from day_data where symbol = '" + stock_symbol + "';"
        cursor1.execute(select_symbol_from_day_data)
        df = None
        df = pd.DataFrame({'count': [], 'open': [], 'close': [], 'low': [], 'high': [], 'volume': []}, index=[])
        # rows = []
        for (nseToken, count, symbol, date, timestamp, open, close, high, low, Volume) in cursor1:
            # print("count: " + str(count))
            row = pd.DataFrame({'count': [count], 'open': [open], 'close': [close], 'low': [low], 'high': [high], 'volume': [Volume]}, index=[date])
            df = pd.concat([df, row])
            # rows.append(row)
        # for i in range(len(rows) - 1, -1, -1):
        #     df = pd.concat([rows[i], df])
        sdf = StockDataFrame.retype(df)
        ema_55 = sdf['close_55_ema']
        rsi_14 = sdf['rsi_14']
        for index in range(0, len(sdf.index)):
            print("index: " + str(index) + ", date: " + sdf.index[index] + ", close_55_ema: " + str(sdf['close_55_ema'][index]) + ", rsi_14: " + str(sdf['rsi_14'][index]))
        # print(sdf)
        # print(sdf['close_55_ema'])
    conn1.close


if_strategy_101_data_exists = util.check_if_table_exists("strategy_101_data")
if not util.check_if_table_exists("strategy_101_data"):
    create_table_query = "CREATE TABLE strategy_101_data(" \
                         "id INT NOT NULL AUTO_INCREMENT, " \
                         "symbol VARCHAR(16) NOT NULL, " \
                         "count INT NOT NULL, " \
                         "date VARCHAR(16) NOT NULL, " \
                         "timestamp VARCHAR(32) NOT NULL, " \
                         "open Double (16, 2) NOT NULL, " \
                         "close Double (16, 2) NOT NULL, " \
                         "high Double (16, 2) NOT NULL, " \
                         "low Double (16, 2) NOT NULL, " \
                         "Volume BIGINT NOT NULL, " \
                         "rsi_14 Double (16, 2) NOT NULL, " \
                         "close_55_ema Double (16, 2) NOT NULL" \
                         "PRIMARY KEY (id));"
    # util.create_table(create_table_query)
prepare_data('CAPLIPOINT')
