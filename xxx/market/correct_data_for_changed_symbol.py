import os
import sys
import util
import time
import getopt
import pandas as pd
from kiteconnect import KiteConnect
from datetime import datetime, timedelta


def main(argv):
    symbol = ''
    token = ''
    try:
        opts, args = getopt.getopt(argv, "h:s:t:", ["help=", "symbol=", "token="])
    except getopt.GetoptError:
        # print("exception occurred")
        print('correct_data_for_changed_symbol.py -s <symbol> -t <token>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print('correct_data_for_changed_symbol.py -s <symbol> -t <token>')
            sys.exit()
        elif opt in ("-s", "--symbol"):
            symbol = arg
        elif opt in ("-t", "--token"):
            token = arg

    if symbol == '' or token == '':
        print("error: symbol and token must be provided.")
        sys.exit(2)

    conn1 = util.mysql_connection()
    if conn1 is not None:
        cursor1 = conn1.cursor()

        update_equity_stocks = "update equityStocks set symbol = '" + symbol + "-BE', nseToken = '" + token + "' where symbol = '" + symbol + "';"
        print("copy-paste the following in master_data_refresh.py:")
        print("cursor.execute(\"" + update_equity_stocks + "\")")
        # print("update_equity_stocks: " + update_equity_stocks)
        cursor1.execute(update_equity_stocks)
        conn1.commit()
        # update_day_data_stocks = "update day_data set symbol = '" + symbol + "-BE', nseToken = '" + token + "' where symbol = '" + symbol + "';"
        # # print("update_day_data_stocks: " + update_day_data_stocks)
        # cursor1.execute(update_day_data_stocks)
        # update_5minute_data_stocks = "update 5minute_data set symbol = '" + symbol + "-BE', nseToken = '" + token + "' where symbol = '" + symbol + "';"
        # # print("update_5minute_data_stocks: " + update_5minute_data_stocks)
        # cursor1.execute(update_5minute_data_stocks)
        # conn1.commit()
    conn1.close


if __name__ == "__main__":
    main(sys.argv[1:])
