import os
import util
import time
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


def method_2(historical_data_thread, symbol_details_array, symbol_details_index):
    thread_start_time = time.time()
    df = pd.DataFrame(historical_data_thread.join())
    symbol_details = symbol_details_array[symbol_details_index]
    id = symbol_details['id']
    symbol = symbol_details['symbol']
    industry = symbol_details['industry']
    category = symbol_details['category']
    nseToken = symbol_details['nseToken']
    sdf = StockDataFrame.retype(df)
    rsi_14 = sdf['rsi_14']
    last_index = sdf.index[len(sdf.index) - 1]
    last_index_date = str(last_index)[0:10]
    day_start_index = last_index_date + " 09:15:00+05:30"
    day_start_idx = None
    for idx in range(len(sdf.index) - 1, -1, -1):
        if str(sdf.index[idx]) == day_start_index:
            day_start_idx = idx
            break
    if sdf['rsi_14'][day_start_idx] > 70:
        for rsi_idx in range(day_start_idx, day_start_idx + 7):
            # for rsi_idx in range(day_start_idx, len(sdf.index) - 1):
            #     if sdf['rsi_14'][rsi_idx] < 60:
            if sdf['open'][rsi_idx] > sdf['close'][rsi_idx]:
                # print("symbol: " + symbol + ", category: " + str(category) + ", timestamp: " + str(sdf.index[rsi_idx]))
                break
    thread_end_time = time.time()
    print("time taken by thread " + str(symbol_details_index + 1) + ": " + str(thread_end_time - thread_start_time))


def method_1(category, interval, min_id, max_id):
    main_start_time = time.time()
    api_key = open(util.baby_0_dir + "txt/api_key.txt", 'r').read()
    api_secret = open(util.baby_0_dir + "txt/api_secret.txt", 'r').read()
    access_token = open(util.baby_0_dir + "txt/access_token.txt", 'r').read()

    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)

    from_date = datetime.strftime(datetime.now()-timedelta(5), '%Y-%m-%d %H:%M:00')
    print("from_date: " + from_date)
    to_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    print("to_date: " + to_date)

    conn1 = util.mysql_connection()
    if conn1 is not None:
        cursor1 = conn1.cursor()
        # select_equity_stocks = "select id, symbol, industry, category, nseToken from equityStocks where nseToken is not NULL and symbol = 'ADANIPORTS';"
        select_equity_stocks = "select id, symbol, industry, category, nseToken from equityStocks where nseToken is not NULL and id >= '" + str(min_id) + "' and id <= '" + str(max_id) + "';"
        # select_equity_stocks = "select id, symbol, industry, category, nseToken from equityStocks where nseToken is not NULL and category >= '" + str(category) + "';"
        cursor1.execute(select_equity_stocks)

        historical_data_thread_array = []
        symbol_details_array = []
        for (id, symbol, industry, category, nseToken) in cursor1:
            symbol_details = {"id": id, "symbol": symbol, "industry": industry, "category": category,
                              "nseToken": nseToken}
            symbol_details_array.append(symbol_details)
            historical_data_thread = util.ThreadWithReturnValue(target=kite.historical_data,
                                                                args=(nseToken, from_date, to_date, '5minute'))
            historical_data_thread.start()
            historical_data_thread_array.append(historical_data_thread)
            time.sleep(0.15)

        main_end_time = time.time()
        print("time consumed to create threads: " + str(main_end_time - main_start_time))
        symbol_details_index = 0
        data_processing_thread_array = []
        for historical_data_thread in historical_data_thread_array:
            data_processing_thread = util.ThreadWithReturnValue(target=method_2, args=(historical_data_thread, symbol_details_array, symbol_details_index))
            data_processing_thread.start()
            data_processing_thread_array.append(data_processing_thread)
            symbol_details_index += 1
        for data_processing_thread in data_processing_thread_array:
            data_processing_thread.join()


start_time = time.time()
method_1(3, '5minute', 1, 757)
end_time = time.time()
print("time consumed for db update: " + str(end_time - start_time))
