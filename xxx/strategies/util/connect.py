base_directory = '/home/sss/Documents/bin/xxx/'
import logging
import mysql.connector as sql
from mysql.connector import Error
from kiteconnect import KiteConnect


def get_kite_connect_obj():
    local_data = open(base_directory + 'connect/base_path/local_data.txt', 'r').read()
    api_key = open(local_data + '/kite_api_key.txt', 'r').read()
    access_token = open(local_data + '/kite_access_token.txt', 'r').read()
    kiteConnectObj = KiteConnect(api_key=api_key)
    kiteConnectObj.set_access_token(access_token)
    return kiteConnectObj


def mysql_connection():
    conn = None
    try:
        conn = sql.connect(host='localhost', user='root', password='root', database='market')
    except Error as e:
        print("Error while connecting to MySQL", e)
    return conn


def get_logger(log_file_name):
    # Create and configure logger
    logging.basicConfig(filename=log_file_name,
                        format='%(asctime)s:%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO,
                        filemode='a+')
    # Creating an object
    logger = logging.getLogger()
    return logger
