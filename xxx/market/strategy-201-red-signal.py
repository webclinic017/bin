import sys
import util
import time
import getopt
import logging
import pandas as pd
from kiteconnect import KiteConnect
from stockstats import StockDataFrame
from datetime import date, datetime, timedelta


number_of_symbols_in_one_db_connection = 7


logger = util.get_logger(util.baby_0_dir + 'txt/strategy-201-red.log')


def get_symbol_details_array(symbols, today_date_str):
    symbol_details_array = []
    conn = util.mysql_connection()
    cursor = conn.cursor()
    if len(symbols) == 0:
        select_equity_stocks = "select id, symbol, category, nseToken from equityStocks_" + today_date_str + " where signal_timestamp is NULL;"
    else:
        symbols_str = ''
        counter = 0
        for symbol in symbols:
            symbols_str += " symbol = '" + symbol + "'"
            if counter < (len(symbols) - 1):
                symbols_str += " or "
            counter = counter + 1
        select_equity_stocks = "select id, symbol, category, nseToken from equityStocks where nseToken is not NULL and" + symbols_str + ";"
    # logger.info("select_equity_stocks: " + select_equity_stocks)
    cursor.execute(select_equity_stocks)
    for (id, symbol, category, nseToken) in cursor:
        symbol_details = {"symbol": symbol, "category": category, "nseToken": nseToken}
        symbol_details_array.append(symbol_details)
    conn.close
    return symbol_details_array


def analyze_historical_data(kite, symbol_details, back_day_scan_start_timestamp, this_day_current_timestamp, interval, today_date_str):
    global signal_limit
    records = kite.historical_data(symbol_details['nseToken'], back_day_scan_start_timestamp, this_day_current_timestamp, interval)
    df = pd.DataFrame(records)
    sdf = StockDataFrame.retype(df)
    rsi_14 = sdf['rsi_14']
    # logger.info("symbol: " + symbol_details['symbol'] + ", sdf: " + str(sdf))
    if sdf['close'][len(sdf.index) - 1] < util.strategy_201_red_stock_max_allowed_price and rsi_14[len(sdf.index) - 1] > util.strategy_201_red_signal_limit:
    # if sdf['close'][len(sdf.index) - 1] < stock_max_allowed_price and rsi_14[len(sdf.index) - 1] > signal_limit:
    #     logger.info("symbol: " + symbol_details['symbol'] + ", previous => timestamp: " + str(sdf.index[len(sdf.index) - 2]) + ", open: " + str(sdf['open'][len(sdf.index) - 2]) + ", close: " + str(sdf['close'][len(sdf.index) - 2]) + ", low: " + str(sdf['low'][len(sdf.index) - 2]) + ", high: " + str(sdf['high'][len(sdf.index) - 2]) + ", volume: " + str(sdf['volume'][len(sdf.index) - 2]) + ", rsi: " + str(rsi_14[len(sdf.index) - 2]))
    #     logger.info("symbol: " + symbol_details['symbol'] + ", signal => timestamp: " + str(sdf.index[len(sdf.index) - 1]) + ", open: " + str(sdf['open'][len(sdf.index) - 1]) + ", close: " + str(sdf['close'][len(sdf.index) - 1]) + ", low: " + str(sdf['low'][len(sdf.index) - 1]) + ", high: " + str(sdf['high'][len(sdf.index) - 1]) + ", volume: " + str(sdf['volume'][len(sdf.index) - 1]) + ", rsi: " + str(rsi_14[len(sdf.index) - 1]))
        update_query = "update equityStocks_" + today_date_str + " set signal_timestamp = '" + (str(
            sdf.index[len(sdf.index) - 1]))[0:19] + "' where symbol = '" + str(symbol_details['symbol']) + "';"
        conn = util.mysql_connection()
        cursor = conn.cursor()
        # logger.info("update_query: " + update_query)
        cursor.execute(update_query)
        conn.commit()
        conn.close


def main(argv):
    interval = '3minute'
    # symbols = ['ASHOKLEY']
    symbols = []
    # today_date = "2021-06-24"
    today_date = datetime.today().strftime('%Y-%m-%d')
    date_vals = str(today_date).split('-')
    today_date_str = date_vals[0] + "_" + date_vals[1] + "_" + date_vals[2]
    symbol_details_array = get_symbol_details_array(symbols, today_date_str)

    kite = util.get_kite()

    back_day_scan_start_timestamp = util.get_back_day_scan_start_timestamp(kite, util.strategy_201_red_timedelta_days)
    # this_day_current_timestamp = "2021-06-24 09:15:30"
    this_day_current_timestamp = str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))


    data_analysis_thread_array = []
    for i in range(0, len(symbol_details_array)):
        symbol_details = symbol_details_array[i]
        # analyze_historical_data(kite, symbol_details, back_day_scan_start_timestamp, this_day_current_timestamp, interval)
        data_analysis_thread = util.ThreadWithReturnValue(target=analyze_historical_data, args=(kite, symbol_details, back_day_scan_start_timestamp, this_day_current_timestamp, interval, today_date_str))
        data_analysis_thread.start()
        data_analysis_thread_array.append(data_analysis_thread)
        time.sleep(0.15)

    for data_analysis_thread in data_analysis_thread_array:
        data_analysis_thread.join()


if __name__ == "__main__":
    time.sleep(30)
    logger.info("strategy-201-red-signal.py started after sleep: " + str(datetime.today().strftime('%Y-%m-%d %H:%M:%S')))
    start_time = time.time()
    main(sys.argv[1:])
    end_time = time.time()
    logger.info("time consumed to run completely: " + str(end_time - start_time))
