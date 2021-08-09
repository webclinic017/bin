import sys
import util
import time
import getopt
import logging
import pandas as pd
from kiteconnect import KiteConnect
from stockstats import StockDataFrame
from datetime import date, datetime, timedelta


logger = util.get_logger(util.baby_0_dir + 'txt/strategy-201-red.log')


def main(argv):
    ids_array = [
        {'category': 5, 'min_id': 1, 'max_id': 50},
        {'category': 4, 'min_id': 51, 'max_id': 100},
        {'category': 3, 'min_id': 101, 'max_id': 200},
        {'category': 2, 'min_id': 201, 'max_id': 501},
        {'category': 1, 'min_id': 502, 'max_id': 757},
        # {'category': 5, 'min_id': 0, 'max_id': 0},
        # {'category': 4, 'min_id': 51, 'max_id': 100},
        # {'category': 3, 'min_id': 101, 'max_id': 200},
        # {'category': 2, 'min_id': 201, 'max_id': 250},
        # {'category': 1, 'min_id': 0, 'max_id': 0},
    ]
    # BE series stocks blocked for MIS
    ids_to_delete = []
    # ids_to_delete = [54, 55, 103, 210, 320, 399, 456, 465, 501, 510, 531, 557, 558, 596, 608, 629, 639, 649, 667, 694, 697, 722, 735, 736, 738]

    kite = util.get_kite()

    conn1 = util.mysql_connection()
    cursor1 = conn1.cursor()

    # today_date = "2021-06-18"
    today_date = datetime.today().strftime('%Y-%m-%d')
    date_vals = str(today_date).split('-')
    today_date_str = date_vals[0] + "_" + date_vals[1] + "_" + date_vals[2]
    logger.info("today_date: " + str(today_date))
    create_new_equityStocks_table_query = "CREATE TABLE equityStocks_" + today_date_str + " AS SELECT * FROM equityStocks where nseToken is not NULL;"
    # logger.info(create_new_equityStocks_table_query)
    cursor1.execute(create_new_equityStocks_table_query)
    ids_delete_str = ''
    counter = 0
    for ids in ids_array:
        ids_delete_str += "(category = '" + str(ids['category']) + "' and (id < '" + str(ids['min_id']) + "' or id > '" + str(ids['max_id']) + "'))"
        if counter < (len(ids_array) - 1):
            ids_delete_str += " or "
        counter = counter + 1
    delete_from_equityStocks_table_query = "delete from equityStocks_" + today_date_str + " where " + ids_delete_str + ";"
    # logger.info(delete_from_equityStocks_table_query)
    cursor1.execute(delete_from_equityStocks_table_query)
    conn1.commit()
    for id_to_delete in ids_to_delete:
        delete_query = "delete from equityStocks_" + today_date_str + " where id = " + str(id_to_delete) + ";"
        cursor1.execute(delete_query)
        conn1.commit()

    add_index_id = "alter table equityStocks_" + today_date_str + " ADD PRIMARY KEY (id);"
    cursor1.execute(add_index_id)
    add_index_symbol = "create index symbol on equityStocks_" + today_date_str + " (symbol);"
    cursor1.execute(add_index_symbol)

    drop_column_bseToken = "alter table equityStocks_" + today_date_str + " drop column bseToken;"
    cursor1.execute(drop_column_bseToken)
    drop_column_industry = "alter table equityStocks_" + today_date_str + " drop column industry;"
    cursor1.execute(drop_column_industry)
    drop_column_companyName = "alter table equityStocks_" + today_date_str + " drop column companyName;"
    cursor1.execute(drop_column_companyName)

    add_column_signal_timestamp = "ALTER TABLE equityStocks_" + today_date_str + " ADD signal_timestamp char(19);"
    cursor1.execute(add_column_signal_timestamp)
    add_column_signal_timestamp = "ALTER TABLE equityStocks_" + today_date_str + " ADD is_blocked int default 0;"
    cursor1.execute(add_column_signal_timestamp)
    add_column_signal_timestamp = "ALTER TABLE equityStocks_" + today_date_str + " ADD confirmation_timestamp char(19);"
    cursor1.execute(add_column_signal_timestamp)
    add_column_signal_timestamp = "ALTER TABLE equityStocks_" + today_date_str + " ADD position_price double(16, 2);"
    cursor1.execute(add_column_signal_timestamp)
    add_column_signal_timestamp = "ALTER TABLE equityStocks_" + today_date_str + " ADD position_volume BIGINT;"
    cursor1.execute(add_column_signal_timestamp)
    add_column_signal_timestamp = "ALTER TABLE equityStocks_" + today_date_str + " ADD stoploss double(16, 2);"
    cursor1.execute(add_column_signal_timestamp)
    add_column_signal_timestamp = "ALTER TABLE equityStocks_" + today_date_str + " ADD target double(16, 2);"
    cursor1.execute(add_column_signal_timestamp)
    add_column_signal_timestamp = "ALTER TABLE equityStocks_" + today_date_str + " ADD stoploss_amount double(16, 2);"
    cursor1.execute(add_column_signal_timestamp)
    add_column_signal_timestamp = "ALTER TABLE equityStocks_" + today_date_str + " ADD target_amount double(16, 2);"
    cursor1.execute(add_column_signal_timestamp)
    add_column_signal_timestamp = "ALTER TABLE equityStocks_" + today_date_str + " ADD position_order_id varchar(32);"
    cursor1.execute(add_column_signal_timestamp)
    add_column_signal_timestamp = "ALTER TABLE equityStocks_" + today_date_str + " ADD target_order_id varchar(32);"
    cursor1.execute(add_column_signal_timestamp)

    d_this = date(int(today_date_str[0:4]), int(today_date_str[5:7]), int(today_date_str[8:10]))
    back_days = timedelta(5)
    d_back = d_this - back_days
    logger.info("d_back: " + str(d_back))
    symbol_data_fetch_counter = 0
    select_equityStocks_query = "select id, symbol, category, nseToken from equityStocks_" + today_date_str + ";"
    cursor1.execute(select_equityStocks_query)
    for (id, symbol, category, nseToken) in cursor1:
        records = kite.historical_data(nseToken, d_back, today_date, 'day')
        df = pd.DataFrame(records)
        # sdf = StockDataFrame.retype(df)
        symbol_data_fetch_counter += 1
        try:
            logger.info(str(id) + ", symbol: " + symbol + ", df['open'][len(df.index) - 1]: " + str(df['open'][len(df.index) - 1]))
        except:
            logger.info(str(id) + ", symbol: " + symbol + ", -------------------------------------------------------------------------------")
    logger.info("symbol_data_fetch_counter: " + str(symbol_data_fetch_counter))


if __name__ == "__main__":
    time.sleep(15)
    logger.info("strategy-201-red-prep.py started after sleep.")
    start_time = time.time()
    main(sys.argv[1:])
    end_time = time.time()
    logger.info("time consumed to run completely: " + str(end_time - start_time))
