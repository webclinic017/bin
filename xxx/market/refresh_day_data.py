## CREATE table day_data(nseToken VARCHAR(16) NOT NULL, count INT NOT NULL, symbol VARCHAR(16) NOT NULL, date VARCHAR(16) NOT NULL, timestamp VARCHAR(32) NOT NULL, open Double (16, 2) NOT NULL, close Double (16, 2) NOT NULL, high Double (16, 2) NOT NULL, low Double (16, 2) NOT NULL, Volume BIGINT NOT NULL, PRIMARY KEY (nseToken, count), KEY idx_symbol (symbol), KEY idx_date (date), KEY idx_timestamp (timestamp));

import os
import sys
import util
import time
import getopt
import pandas as pd
from kiteconnect import KiteConnect
from datetime import datetime, timedelta


max_data_fetching_time = 0
max_db_operations_time = 0


def update_db(historical_data_thread_array, start_index, end_index, symbol_details_array, data_timing_set, data_table, db_update_conn, db_update_cursor, thread_start_time_array):
    global max_data_fetching_time
    global max_db_operations_time
    symbol_details_index = 0
    for i in range(start_index, end_index):
        historical_data_thread = historical_data_thread_array[i]
        df = pd.DataFrame(historical_data_thread.join())
        data_received_at = time.time()
        symbol_details_final_index = start_index + symbol_details_index
        if (data_received_at - thread_start_time_array[symbol_details_final_index]) > max_data_fetching_time:
            max_data_fetching_time = (data_received_at - thread_start_time_array[symbol_details_final_index])
        # print("time taken in fetching data for index " + str(symbol_details_final_index) + " : " + str(data_received_at - thread_start_time_array[symbol_details_final_index]))
        symbol_details = symbol_details_array[symbol_details_final_index]
        symbol_details_index += 1
        id = symbol_details['id']
        symbol = symbol_details['symbol']
        industry = symbol_details['industry']
        category = symbol_details['category']
        nseToken = symbol_details['nseToken']
        for index, row in df.iterrows():
            timestamp = str(row['date'])
            timestamp_date = timestamp[0:10]
            timestamp_time = timestamp[11:19]
            candle_timestamp = timestamp[0:19]
            # print("date: " + timestamp_date)
            # print("time: " + timestamp_time)
            if timestamp_time in data_timing_set:
                open_val = str(row['open'])
                high = str(row['high'])
                low = str(row['low'])
                close = str(row['close'])
                volume = str(row['volume'])
                select_data_query = "select count from " + data_table + " where symbol = '" + symbol + "' and date = '" + timestamp_date + "' and time = '" + timestamp_time + "';"
                # print("select_data_query: " + select_data_query)
                db_update_cursor.execute(select_data_query)
                count_row = db_update_cursor.fetchone()
                # symbol_date_count = 0
                if count_row is not None:
                    symbol_date_count = count_row[0]
                    update_data_query = "update " + data_table + " set open = '" + str(open_val) + "', close = '" + str(
                        close) + "', high = '" + str(high) + "', low = '" + str(low) + "', volume = '" + str(
                        volume) + "' where symbol = '" + symbol + "' and count = '" + str(symbol_date_count) + "';"
                    # print("update_5minute_data: " + update_5minute_data)
                    db_update_cursor.execute(update_data_query)
                    db_update_conn.commit()
                else:
                    symbol_next_count = None
                    select_data_query = "select max(count) from " + data_table + " where symbol = '" + symbol + "';"
                    # print("select_5minute_data: " + select_5minute_data)
                    db_update_cursor.execute(select_data_query)
                    max_count_row = db_update_cursor.fetchone()
                    if max_count_row[0] is None:
                        symbol_next_count = 1
                    else:
                        symbol_next_count = max_count_row[0] + 1
                    insert_data_query = "insert into " + data_table + " (symbol, count, date, time, open, close, high, low, volume) values ('" + symbol + "', '" + str(
                        symbol_next_count) + "', '" + timestamp_date + "', '" + timestamp_time + "', '" + str(
                        open_val) + "', '" + str(close) + "', '" + str(high) + "', '" + str(low) + "', '" + str(volume) + "');"
                    # insert_data_query = "insert into " + data_table + " (symbol, count, date, time, candle_timestamp, open, close, high, low, volume) values ('" + symbol + "', '" + str(
                    #     symbol_next_count) + "', '" + timestamp_date + "', '" + timestamp_time + "', '" + candle_timestamp + "', '" + str(
                    #     open_val) + "', '" + str(close) + "', '" + str(high) + "', '" + str(low) + "', '" + str(volume) + "');"
                    # print("insert_5minute_data: " + insert_5minute_data)
                    db_update_cursor.execute(insert_data_query)
                    db_update_conn.commit()
        db_operations_completed_at = time.time()
        # print("time taken in db operations for index " + str(symbol_details_final_index) + " : " + str(db_operations_completed_at - data_received_at))
        if max_db_operations_time < (db_operations_completed_at - data_received_at):
            max_db_operations_time = (db_operations_completed_at - data_received_at)
    db_update_conn.close


def main(argv):
    main_start_time = time.time()
    # stock_symbols = []
    # stock_symbols = ['RELIANCE']
    stock_symbols = ['ADANIPORTS', 'ASIANPAINT', 'AXISBANK', 'BAJAJ-AUTO', 'BAJFINANCE']
    # stock_symbols = ['ADANIPORTS', 'ASIANPAINT', 'AXISBANK', 'BAJAJ-AUTO', 'BAJFINANCE', 'BAJAJFINSV']
    # stock_symbols = ['ADANIPORTS', 'ASIANPAINT', 'AXISBANK', 'BAJAJ-AUTO', 'BAJFINANCE', 'BAJAJFINSV', 'BPCL']
    # stock_symbols = ['ADANIPORTS', 'ASIANPAINT', 'AXISBANK', 'BAJAJ-AUTO', 'BAJFINANCE', 'BAJAJFINSV', 'BPCL', 'BHARTIARTL']
    # stock_symbols = ['ADANIPORTS', 'ASIANPAINT', 'AXISBANK', 'BAJAJ-AUTO', 'BAJFINANCE', 'BAJAJFINSV', 'BPCL', 'BHARTIARTL', 'BRITANNIA', 'CIPLA']

    number_of_symbols_in_one_db_connection = 7

    # if os.stat(util.baby_0_dir + "txt/changed_symbols.txt").st_size != 0:
    #     print("changed symbols present.")
    #     sys.exit(2)
    # interval = ''
    interval = '5minute'
    number_of_back_days_to_refresh = 0
    symbol_source_table = 'equityStocks'
    try:
        opts, args = getopt.getopt(argv, "h:i:d:t:", ["help=", "interval=", "days=", "table="])
    except getopt.GetoptError:
        # print("exception occurred")
        print('refresh_day_data.py -i <interval> -d <number_of_back_days_to_refresh> -t <symbol_source_table>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print('refresh_day_data.py -i <interval> -d <number_of_back_days_to_refresh> -t <symbol_source_table>')
            sys.exit()
        elif opt in ("-i", "--interval"):
            interval = arg
        elif opt in ("-d", "--days"):
            number_of_back_days_to_refresh = int(arg)
        elif opt in ("-t", "--table"):
            symbol_source_table = arg
    if interval == '':
        print("interval must be provided.")
        sys.exit(2)
    data_table = interval + "_data"

    api_key = open(util.baby_0_dir + "txt/api_key.txt", 'r').read()
    api_secret = open(util.baby_0_dir + "txt/api_secret.txt", 'r').read()
    access_token = open(util.baby_0_dir + "txt/access_token.txt", 'r').read()
    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)

    conn1 = util.mysql_connection()
    cursor1 = conn1.cursor()
    conn2 = util.mysql_connection()
    cursor2 = conn2.cursor()

    # create a data_timing_set
    data_timing_set = set()
    select_data_timing_query = "select * from data_timing where data_interval = '" + interval + "';"
    cursor1.execute(select_data_timing_query)
    for (data_interval, timing) in cursor1:
        data_timing_set.add(timing)

    # check if data table exists or not. if not, then create one
    data_table_exist_query = "SHOW TABLES LIKE '" + data_table + "';"
    cursor1.execute(data_table_exist_query)
    data_table_exist_row = cursor1.fetchone()
    if data_table_exist_row is None:
        create_data_table_query = "CREATE table " + data_table + "(symbol VARCHAR(16) NOT NULL, count INT NOT NULL, date VARCHAR(16) NOT NULL, time VARCHAR(16) NOT NULL, open Double (16, 2) NOT NULL, close Double (16, 2) NOT NULL, high Double (16, 2) NOT NULL, low Double (16, 2) NOT NULL, Volume BIGINT NOT NULL, PRIMARY KEY (symbol, count), KEY idx_date (date), KEY idx_time (time));"
        # create_data_table_query = "CREATE table " + data_table + "(symbol VARCHAR(16) NOT NULL, count INT NOT NULL, date VARCHAR(16) NOT NULL, time VARCHAR(16) NOT NULL, candle_timestamp TIMESTAMP NOT NULL, open Double (16, 2) NOT NULL, close Double (16, 2) NOT NULL, high Double (16, 2) NOT NULL, low Double (16, 2) NOT NULL, Volume BIGINT NOT NULL, PRIMARY KEY (symbol, count), KEY idx_date (date), KEY idx_time (time), KEY idx_candle_timestamp (candle_timestamp));"
        cursor2.execute(create_data_table_query)

    # fetch the symbols, for which we need to run the data
    select_equity_stocks = ''
    if len(stock_symbols) == 0:
        select_equity_stocks = "select id, symbol, industry, category, nseToken from " + symbol_source_table + " where nseToken is not NULL;"
    else:
        symbols_str = ''
        counter = 0
        for stock_symbol in stock_symbols:
            symbols_str += " symbol = '" + stock_symbol + "'"
            if counter < (len(stock_symbols) - 1):
                symbols_str += " or"
            counter = counter + 1
        select_equity_stocks = "select id, symbol, industry, category, nseToken from equityStocks where nseToken is not NULL and" + symbols_str + ";"
    # print("select_equity_stocks: " + select_equity_stocks)
    cursor1.execute(select_equity_stocks)

    thread_start_time_array = []
    historical_data_thread_array = []
    symbol_details_array = []
    for (id, symbol, industry, category, nseToken) in cursor1:
        symbol_details = {"id": id, "symbol": symbol, "industry": industry, "category": category, "nseToken": nseToken}
        # print('symbol_details: ' + str(symbol_details))
        symbol_details_array.append(symbol_details)
        select_from_time_query = "select date, time from " + data_table + " where symbol = '" + symbol + "' and count = (select max(count) from " + data_table + " where symbol = '" + symbol + "');"
        # print("select_from_time_query: " + select_from_time_query)
        cursor2.execute(select_from_time_query)
        select_from_time_val = cursor2.fetchone()
        from_date = ''
        if select_from_time_val is None:
            from_date = datetime.strftime(datetime.now() - timedelta(util.available_historical_data_max_days_dictionary[interval]), '%Y-%m-%d 00:00:00')
        else:
            from_date = select_from_time_val[0] + " " + select_from_time_val[1]
        to_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        historical_data_thread = util.ThreadWithReturnValue(target=kite.historical_data, args=(nseToken, from_date, to_date, interval))
        historical_data_thread.start()
        thread_start_time_array.append(time.time())
        historical_data_thread_array.append(historical_data_thread)
        time.sleep(0.15)
    thread_creation_end_time = time.time()
    print("time taken in creation of thread: " + str(thread_creation_end_time - main_start_time))

    db_update_thread_array = []
    data_thread_array_length = len(historical_data_thread_array)
    data_thread_processing_index = 0
    while data_thread_processing_index <= data_thread_array_length:
        start_index = data_thread_processing_index
        end_index = 0
        if data_thread_processing_index + number_of_symbols_in_one_db_connection <= data_thread_array_length:
            end_index = data_thread_processing_index + number_of_symbols_in_one_db_connection
        else:
            end_index = data_thread_array_length
        db_update_conn = util.mysql_connection()
        db_update_cursor = db_update_conn.cursor()
        # update_db(historical_data_thread_array, start_index, end_index, symbol_details_array, data_timing_set, data_table, db_update_conn, db_update_cursor)
        db_update_thread = util.ThreadWithReturnValue(target=update_db,
                                                            args=(historical_data_thread_array, start_index, end_index, symbol_details_array, data_timing_set, data_table, db_update_conn, db_update_cursor, thread_start_time_array))
        db_update_thread.start()
        db_update_thread_array.append(db_update_thread)
        data_thread_processing_index += number_of_symbols_in_one_db_connection

    for db_update_thread in db_update_thread_array:
        db_update_thread.join()

    conn2.close
    conn1.close


if __name__ == "__main__":
    start_time = time.time()
    main(sys.argv[1:])
    end_time = time.time()
    print("total time consumed: " + str(end_time - start_time))
    print("max_data_fetching_time: " + str(max_data_fetching_time))
    print("max_db_operations_time: " + str(max_db_operations_time))
