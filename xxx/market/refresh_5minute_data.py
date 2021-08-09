# CREATE table 5minute_data(nseToken VARCHAR(16) NOT NULL, count INT NOT NULL, symbol VARCHAR(16) NOT NULL, date VARCHAR(16) NOT NULL, time VARCHAR(16) NOT NULL, open Double (16, 2) NOT NULL, close Double (16, 2) NOT NULL, high Double (16, 2) NOT NULL, low Double (16, 2) NOT NULL, Volume BIGINT NOT NULL, PRIMARY KEY (nseToken, count), KEY idx_symbol (symbol), KEY idx_date(date), KEY idx_time(time));

import os
import sys
import util
import time
import getopt
import pandas as pd
from kiteconnect import KiteConnect
from datetime import datetime, timedelta


def main(argv):
    main_start_time = time.time()
    number_of_back_candles_to_refresh = 0
    try:
        opts, args = getopt.getopt(argv, "h:n:", ["help="])
    except getopt.GetoptError:
        # print("exception occurred")
        print('refresh_5minute_data.py -n <number_of_back_candles_to_refresh>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print('refresh_5minute_data.py -n <number_of_back_candles_to_refresh>')
            sys.exit()
        elif opt in ("-n", "--number"):
            number_of_back_candles_to_refresh = int(arg)

    # stock_symbols = []
    stock_symbols = ['PNBHOUSING-BE']
    # stock_symbols = ['ADANIPORTS', 'ASIANPAINT', 'AXISBANK', 'BAJAJ-AUTO', 'BAJFINANCE', 'BAJAJFINSV', 'BPCL', 'BHARTIARTL', 'BRITANNIA', 'CIPLA']
    days_val = number_of_back_candles_to_refresh

    cwd = os.getcwd()
    print("cwd: " + cwd)
    api_key = open(cwd + "/txt/api_key.txt", 'r').read()
    api_secret = open(cwd + "/txt/api_secret.txt", 'r').read()
    access_token = open(cwd + "/txt/access_token.txt", 'r').read()

    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)

    from_date = datetime.strftime(datetime.now()-timedelta(days_val), '%Y-%m-%d 00:00:00')
    print("from_date: " + from_date)
    to_date = datetime.today().strftime('%Y-%m-%d 23:59:59')
    print("to_date: " + to_date)

    conn1 = util.mysql_connection()
    conn2 = util.mysql_connection()
    if conn1 and conn2 is not None:
        cursor1 = conn1.cursor()
        cursor2 = conn2.cursor()

        select_equity_stocks = ''
        if len(stock_symbols) == 0:
            select_equity_stocks = "select id, symbol, industry, category, nseToken from equityStocks where nseToken is not NULL;"
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

        historical_data_thread_array = []
        symbol_details_array = []
        for (id, symbol, industry, category, nseToken) in cursor1:
            symbol_details = {"id" : id, "symbol" : symbol, "industry" : industry, "category" : category, "nseToken" : nseToken}
            symbol_details_array.append(symbol_details)
            historical_data_thread = util.ThreadWithReturnValue(target=kite.historical_data, args=(nseToken, from_date, to_date, '5minute'))
            historical_data_thread.start()
            historical_data_thread_array.append(historical_data_thread)
            time.sleep(0.15)

        main_end_time = time.time()
        print("time consumed to create threads: " + str(main_end_time - main_start_time))
        symbol_data_max_length = 0
        symbol_data_length_array = []
        symbol_details_index = 0
        for historical_data_thread in historical_data_thread_array:
            df = pd.DataFrame(historical_data_thread.join())
            symbol_details = symbol_details_array[symbol_details_index]
            symbol_details_index += 1
            id = symbol_details['id']
            symbol = symbol_details['symbol']
            industry = symbol_details['industry']
            category = symbol_details['category']
            nseToken = symbol_details['nseToken']

            if len(df.index) > symbol_data_max_length:
                symbol_data_max_length = len(df.index)
            symbol_data_length = {"symbol" : symbol, "data_length" : len(df.index)}
            symbol_data_length_array.append(symbol_data_length)

            print("symbol: " + symbol)
            for index, row in df.iterrows():
                timestamp = str(row['date'])
                timestamp_date = timestamp[0:10]
                timestamp_time = timestamp[11:19]
                # print("date: " + timestamp_date)
                # print("time: " + timestamp_time)
                open_val = str(row['open'])
                high = str(row['high'])
                low = str(row['low'])
                close = str(row['close'])
                volume = str(row['volume'])
                select_5minute_data = "select count from 5minute_data where nseToken = '" + nseToken + "' and date = '" + timestamp_date + "' and time = '" + timestamp_time + "';"
                # print("select_5minute_data: " + select_5minute_data)
                cursor2.execute(select_5minute_data)
                count_row = cursor2.fetchone()
                symbol_date_count = 0
                if count_row is not None:
                    symbol_date_count = count_row[0]
                    update_5minute_data = "update 5minute_data set open = '" + str(open_val) + "', close = '" + str(close) + "', high = '" + str(high) + "', low = '" + str(low) + "', volume = '" + str(volume) + "' where nseToken = '" + nseToken + "' and count = '" + str(symbol_date_count) + "';"
                    # print("update_5minute_data: " + update_5minute_data)
                    cursor2.execute(update_5minute_data)
                    conn2.commit()
                else:
                    symbol_next_count = None
                    select_5minute_data = "select max(count) from 5minute_data where nseToken = '" + nseToken + "';"
                    # print("select_5minute_data: " + select_5minute_data)
                    cursor2.execute(select_5minute_data)
                    max_count_row = cursor2.fetchone()
                    if max_count_row[0] is None:
                        symbol_next_count = 1
                    else:
                        symbol_next_count = max_count_row[0] + 1
                    insert_5minute_data = "insert into 5minute_data (nseToken, count, symbol, date, time, open, close, high, low, volume) values ('" + nseToken + "', '" + str(symbol_next_count) + "', '" + symbol + "', '" + timestamp_date + "', '" + timestamp_time + "', '" + str(open_val) + "', '" + str(close) + "', '" + str(high) + "', '" + str(low) + "', '" + str(volume) + "');"
                    # print("insert_5minute_data: " + insert_5minute_data)
                    cursor2.execute(insert_5minute_data)
                    conn2.commit()

        for symbol_data_length in symbol_data_length_array:
            if symbol_data_length['data_length'] < symbol_data_max_length:
                print("less data coming for symbol: " + symbol_data_length['symbol'])

    conn2.close
    conn1.close


if __name__ == "__main__":
    start_time = time.time()
    main(sys.argv[1:])
    end_time = time.time()
    print("time consumed to run: " + str(end_time - start_time))
