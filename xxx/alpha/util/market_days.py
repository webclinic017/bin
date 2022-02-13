import time
import thread
import connect
import pandas as pd
from stockstats import StockDataFrame
from datetime import date, datetime, timedelta

number_of_days_to_check = 5
# number_of_days_to_check = 365 * 5
kite = connect.get_kite_connect_obj()


def check_if_a_market_day(day):
    # print("date: " + day)
    conn = connect.mysql_connection()
    historical_data_thread_array = []
    symbol_array = []
    if conn is not None:
        cursor = conn.cursor()
        select_equity_stocks = "select id, symbol, nseToken from equityStocks where category = '5' limit 11;"
        cursor.execute(select_equity_stocks)
        rows = cursor.fetchall()
        cursor.close()
        for row in rows:
            symbol_array.append(row[1])
            historical_data_thread = thread.ThreadWithReturnValue(target=kite.historical_data, args=(str(row[2]), day, day, 'day'))
            historical_data_thread.start()
            historical_data_thread_array.append(historical_data_thread)
            time.sleep(0.15)
    array_of_stocks_having_data = []
    array_of_stocks_having_no_data = []
    itr = 0
    for historical_data_thread in historical_data_thread_array:
        symbol = symbol_array[itr]
        itr = itr + 1
        df = pd.DataFrame(historical_data_thread.join())
        sdf = StockDataFrame.retype(df)
        if sdf.index.size > 0:
            array_of_stocks_having_data.append(symbol)
        else:
            array_of_stocks_having_no_data.append(symbol)
    if len(array_of_stocks_having_data) == 11:
        return 1
    elif len(array_of_stocks_having_no_data) == 11:
        return -1
    else:
        print("array_of_stocks_having_data: ")
        print(array_of_stocks_having_data)
        print("array_of_stocks_having_no_data: ")
        print(array_of_stocks_having_no_data)
        print("")
        return 0


def fill_scan_date_array_from_the_day(day):
    scan_date_array = []
    scan_end_date = date(int(day[0:4]), int(day[5:7]), int(day[8:10]))
    scan_start_date = scan_end_date - timedelta(days=(number_of_days_to_check - 1))
    num_days = scan_end_date - scan_start_date
    temp_scan_date_array = []
    for i in range(num_days.days + 1):
        day = scan_end_date - timedelta(days=i)
        temp_scan_date_array.append(str(day))
    for scan_date in reversed(temp_scan_date_array):
        scan_date_array.append(scan_date)
    return scan_date_array


def populate_db_table_market_days(scan_date_array):
    for scan_date in scan_date_array:
        # print("scan_date: " + scan_date)
        conn1 = connect.mysql_connection()
        if conn1 is not None:
            rows1 = market_days_rows(conn1, scan_date)
            if not rows1:
                is_market_day = check_if_a_market_day(scan_date)
                insert_market_days = "INSERT INTO market_days (date, is_a_market_day) values ('" + scan_date + "', '" + str(is_market_day) + "');"
                # print(insert_market_days)
                conn2 = connect.mysql_connection()
                if conn2 is not None:
                    cursor2 = conn2.cursor()
                    cursor2.execute(insert_market_days)
                    cursor2.close()
                    conn2.commit()
                    conn2.close()
            # else:
            #     for row in rows1:
            #         print("date: " + row[0] + ", is_a_market_day: " + str(row[1]))
            conn1.close()


def market_days_rows(conn, day):
    cursor = conn.cursor()
    select_market_days = "select date, is_a_market_day from market_days where date = '" + day + "';"
    # print("select_market_days: " + select_market_days)
    cursor.execute(select_market_days)
    rows = cursor.fetchall()
    cursor.close()
    return rows


def is_a_market_day_with_conn(conn, day):
    rows = market_days_rows(conn, day)
    if not rows:
        scan_date_array = fill_scan_date_array_from_the_day(day)
        populate_db_table_market_days(scan_date_array)
        new_conn = connect.mysql_connection()
        rows = market_days_rows(new_conn, day)
        new_conn.close()
    first_row = rows[0]
    if first_row[1] == 1:
        # print("True")
        return True
    else:
        # print("False")
        return False


def is_a_market_day_without_conn(day):
    conn = connect.mysql_connection()
    is_a_market_day = is_a_market_day_with_conn(conn, day)
    conn.close()
    return is_a_market_day


is_a_market_day_without_conn('2022-02-13')
