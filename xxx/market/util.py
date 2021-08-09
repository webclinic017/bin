import pandas as pd
import sys
import getopt
import logging
import threading
import mysql.connector as sql
from mysql.connector import Error
from kiteconnect import KiteConnect
from datetime import date, datetime, timedelta
from stockstats import StockDataFrame


baby_0_dir = '/home/shubham/PycharmProjects/baby-0/'
available_historical_data_max_days_dictionary = {'day' : 0, 'minute' : 60, '3minute' : 100, '5minute' : 20, '10minute' : 100, '15minute' : 200, '30minute' : 200, '60minute' : 400}
stock_max_allowed_price = 5000
strategy_201_red_timedelta_days = 3
strategy_201_red_signal_limit = 70
strategy_201_red_stock_max_allowed_price = 5000
strategy_201_red_min_per_minute_trade = 1000

strategy_211_rsi_upper_limit = 60
strategy_211_rsi_lower_limit = 40
strategy_211_max_amount_allowed_in_one_stock = 100000
strategy_211_volume_multiplier = 0.005    # can't be greater than 0.05
strategy_211_min_per_minute_trade = 100

strategy_212_max_amount_allowed_in_one_stock = 25000
strategy_212_target_percentage = 0.5
strategy_212_volume_multiplier = 0.005    # can't be greater than 0.05
strategy_212_min_per_minute_trade = 100


class ThreadWithReturnValue(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        threading.Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        # print(type(self._target))
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        threading.Thread.join(self, *args)
        return self._return


def get_kite():
    api_key = open(baby_0_dir + "txt/api_key.txt", 'r').read()
    api_secret = open(baby_0_dir + "txt/api_secret.txt", 'r').read()
    access_token = open(baby_0_dir + "txt/access_token.txt", 'r').read()
    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)
    return kite


def mysql_connection():
    conn = None
    try:
        conn = sql.connect(host='localhost', user='root', password='root', database='market')
    except Error as e:
        print("Error while connecting to MySQL", e)
    return conn


def get_back_day_scan_start_timestamp(kite, number_of_days_back):
    # 738561 is nseToken of RELIANCE.
    from_date = datetime.strftime(datetime.now() - timedelta(10), '%Y-%m-%d')
    to_date = datetime.today().strftime('%Y-%m-%d')
    records = kite.historical_data('738561', from_date, to_date, 'day')
    df = pd.DataFrame(records)
    sdf = StockDataFrame.retype(df)
    sdf_scan_start_day_index = len(sdf.index) - number_of_days_back
    sdf_index = sdf.index
    sdf_index_scan_start_day_timestamp = sdf.index[sdf_scan_start_day_index]
    return (str(sdf.index[sdf_scan_start_day_index]))[0:19]


def get_strategy_211_yesterday_date(kite, today_date):
    # 738561 is nseToken of RELIANCE.
    backtest_dates = []
    today_date_obj = date(int(today_date[0:4]), int(today_date[5:7]), int(today_date[8:10]))
    from_date = datetime.strftime(today_date_obj - timedelta(10), '%Y-%m-%d')
    records = kite.historical_data('738561', from_date, today_date, 'day')
    df = pd.DataFrame(records)
    sdf = StockDataFrame.retype(df)
    last_date = str(sdf.index[len(sdf.index) - 1])
    if str(today_date) in last_date:
        last_date = str(sdf.index[len(sdf.index) - 2])
    return last_date[0:10]


def get_strategy_211_scan_dates(kite, number_of_days_back):
    # 738561 is nseToken of RELIANCE.
    backtest_dates = []
    from_date = datetime.strftime(datetime.now() - timedelta(number_of_days_back), '%Y-%m-%d')
    to_date = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
    records = kite.historical_data('738561', from_date, to_date, 'day')
    df = pd.DataFrame(records)
    sdf = StockDataFrame.retype(df)
    for indx in sdf.index:
        backtest_dates.append((str(indx))[0:10])
    return backtest_dates


def get_logger(log_file_name):
    # Create and configure logger
    logging.basicConfig(filename=log_file_name,
                        format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO,
                        filemode='a+')
    # Creating an object
    logger = logging.getLogger()
    return logger


def check_if_table_exists(tableName):
    conn = mysql_connection()
    cursor = conn.cursor()
    stmt = "SHOW TABLES LIKE '" + tableName + "';"
    cursor.execute(stmt)
    result = cursor.fetchone()
    conn.close
    if result:
        return True
    else:
        return False


def create_table(stmt):
    conn = mysql_connection()
    cursor = conn.cursor()
    cursor.execute(stmt)
    conn.close


def get_sdf_dates(sdf):
    dates = []
    for row in sdf.iterrows():
        dates.append((str(row[0]))[0:10])
    return dates


def get_sdf_timestamps(sdf):
    timestamps = []
    for row in sdf.iterrows():
        timestamps.append(str(row[0]))
    return timestamps


def is_crossing_close_55_ema(sdf, today_index):
    today_date = str(sdf.index[today_index])
    sdf_low_today_index = sdf['low'][today_index]
    sdf_close_55_ema = sdf['close_55_ema'][today_index]
    sdf_high_today_index = sdf['high'][today_index]
    if sdf['low'][today_index] < sdf['close_55_ema'][today_index] < sdf['high'][today_index]:
        return True
    else:
        return False


def is_crossing_jump_valid(sdf, starting_index, today_index, jump_limit):
    # starting_date = str(sdf.index[starting_index])
    # today_date = str(sdf.index[today_index])
    index = starting_index
    while index <= today_index:
        open_price = sdf['open'][index]
        close_price = sdf['close'][index]
        jump = close_price - open_price
        percentage_jump = (jump * 100) / close_price
        if percentage_jump >= jump_limit:
            return False
        index = index + 1
    return True


def is_green(sdf, today_index):
    sdf_open_today_index = sdf['open'][today_index]
    sdf_close_today_index = sdf['close'][today_index]
    if sdf['open'][today_index] > sdf['close'][today_index]:
        return False
    else:
        return True


def are_all_green(sdf, from_index, to_index):
    while from_index <= to_index:
        sdf_open_from_index = sdf['open'][from_index]
        sdf_close_from_index = sdf['close'][from_index]
        if sdf['open'][from_index] >= sdf['close'][from_index]:
            return False
        from_index += 1
    return True


def max_array(sdf, attributes):
    max_array = []
    for index in range(0, len(sdf.index)):
        max = float('-inf')
        for attribute in attributes:
            if sdf[attribute][index] > max:
                max = sdf[attribute][index]
        max_array.append(max)
    return max_array


def min_array(sdf, attributes):
    min_array = []
    for index in range(0, len(sdf.index)):
        min = float('inf')
        for attribute in attributes:
            if sdf[attribute][index] < min:
                min = sdf[attribute][index]
        min_array.append(min)
    return min_array


# parameters: ([23, 25, 15, 17], 0, 5)
def is_continuously_increasing(values, from_index, to_index):
    if (from_index >= to_index):
        return True
    for index in range(from_index, to_index):
        # values_from_index = values[index]
        # values_from_index_plus_one = values[index + 1]
        if values[index] > values[index + 1]:
            return False;
    return True


# parameters: (df, ['age', 'salary', 'height'], 0, 5)
def is_any_attribute_continuously_increasing(sdf, attributes, from_index, to_index):
    for attribute in attributes:
        if is_continuously_increasing(values, from_index, to_index):
            return True
    return False


# parameters: (df, ['age', 'salary', 'height'], 0, 5)
def are_all_attributes_continuously_increasing(sdf, attributes, from_index, to_index):
    for attribute in attributes:
        if not is_continuously_increasing(values, from_index, to_index):
            return False
    return True


def get_buying_price(sdf, index, buying_price_strategy):
    close_val = sdf['close'][index]
    high_val = sdf['high'][index]
    if buying_price_strategy == 1:
        return sdf['close'][index]
    if buying_price_strategy == 0:
        return (sdf['high'][index] + sdf['close'][index]) / 2
    if buying_price_strategy == -1:
        return sdf['high'][index]


def get_sell_details(sdf, today_index, buying_price, stoploss, target):
    number_of_days = 0
    selling_price = buying_price
    selling_date = ""
    sdf_length = len(sdf.index)
    is_stoploss_or_target_got_hit = False
    for day_index in range(today_index, sdf_length):
        if sdf['low'][day_index] < stoploss:
            selling_price = stoploss
            selling_date = str(sdf.index[day_index])
            is_stoploss_or_target_got_hit = True
            break
        if sdf['high'][day_index] > target:
            selling_price = target
            selling_date = str(sdf.index[day_index])
            is_stoploss_or_target_got_hit = True
            break
        number_of_days += 1
    if not is_stoploss_or_target_got_hit:
        selling_date = str(sdf.index[sdf_length - 1])
    selling_date_str = selling_date[0:10]
    return selling_price, selling_date_str, number_of_days


def get_number_of_days_for_sell(sdf, today_index, buying_price, stoploss, target):
    number_of_days = 0
    sdf_length = len(sdf.index)
    for index in range(today_index, sdf_length):
        if sdf['low'][index] < stoploss:
            break
        if sdf['high'][index] > target:
            break
        number_of_days = number_of_days + 1
    return number_of_days
