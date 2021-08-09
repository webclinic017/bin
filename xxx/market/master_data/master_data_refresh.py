import os
import util
import pandas as pd

master_data_file_dir = "/tmp/master_data_refresh_downloads"


def create_indnifty_table_and_store_master_data(fileName, tableName, cursor):
    create_temp_table = "CREATE TABLE " + tableName + " (id INT NOT NULL AUTO_INCREMENT, symbol VARCHAR(255) NOT NULL, companyName VARCHAR(255) NOT NULL, industry VARCHAR(255) NOT NULL, PRIMARY KEY (id));"
    print("create_temp_table: " + create_temp_table)
    cursor.execute(create_temp_table)

    tableNameData = pd.read_csv(master_data_file_dir + "/" + fileName)
    tableNameData.drop('Series', inplace=True, axis=1)
    tableNameData.drop('ISIN Code', inplace=True, axis=1)
    tableNameData.head()
    for i, row in tableNameData.iterrows():
        sql = "INSERT INTO " + tableName + " (companyName, industry, symbol) VALUES (%s,%s,%s);"
        cursor.execute(sql, tuple(row))


def create_instruments_table_and_store_master_data(fileName, tableName, cursor):
    create_temp_table = "CREATE TABLE " + tableName + " (id INT NOT NULL AUTO_INCREMENT, instrument_token VARCHAR(255) NOT NULL, trading_symbol VARCHAR(255) NOT NULL, instrument_type VARCHAR(255) NOT NULL, exchange VARCHAR(255) NOT NULL, PRIMARY KEY (id));"
    print("create_temp_table: " + create_temp_table)
    cursor.execute(create_temp_table)

    tableNameData = pd.read_csv(master_data_file_dir + "/" + fileName)
    tableNameData.drop('exchange_token', inplace=True, axis=1)
    tableNameData.drop('name', inplace=True, axis=1)
    tableNameData.drop('last_price', inplace=True, axis=1)
    tableNameData.drop('expiry', inplace=True, axis=1)
    tableNameData.drop('strike', inplace=True, axis=1)
    tableNameData.drop('tick_size', inplace=True, axis=1)
    tableNameData.drop('lot_size', inplace=True, axis=1)
    tableNameData.drop('segment', inplace=True, axis=1)
    tableNameData.head()
    counter = 0
    for i, row in tableNameData.iterrows():
        sql = "INSERT INTO " + tableName + " (instrument_token, trading_symbol, instrument_type, exchange) VALUES (%s, %s, %s, %s);"
        cursor.execute(sql, tuple(row))
        counter = counter + 1
        if (counter % 1000 == 0):
            print("counter: " + str(counter))


def download_and_process_master_data_files(file_type):
    conn1 = util.mysql_connection()
    if conn1 is not None:
        cursor1 = conn1.cursor()
        select_master_data_downloads = "select * from master_data_downloads where type = '" + file_type + "';"
        cursor1.execute(select_master_data_downloads)
        for (id, type, name, link) in cursor1:
            print("id: " + str(id) + ", type: " + type + ", name: " + name + ", link: " + link)
            os.system("curl " + link + " > " + master_data_file_dir + "/" + name)
            tableName = None
            if name.find(".csv") != -1:
                csvIndex = name.index('.csv')
                tableName = name[0:csvIndex]
            else:
                tableName = name
            print('===============================================')
            print(tableName)
            print('###############################################')

            conn2 = util.mysql_connection()
            cursor2 = conn2.cursor()
            drop_temp_table = "drop table if exists " + tableName + ";"
            print("drop_temp_table: " + drop_temp_table)
            cursor2.execute(drop_temp_table)
            if file_type == "ind_nifty":
                create_indnifty_table_and_store_master_data(name, tableName, cursor2)
            if file_type == "kite_token":
                create_instruments_table_and_store_master_data(name, tableName, cursor2)

            conn2.commit()
            conn2.close
    conn1.close


def populate_equity_stocks_with_ind_nifty(tableName, category):
    conn1 = util.mysql_connection()
    if conn1 is not None:
        cursor1 = conn1.cursor()
        select_query = "select * from " + tableName + ";"
        cursor1.execute(select_query)
        for (id, symbol, companyName, industry) in cursor1:
            print("id: " + str(id) + ", symbol: " + symbol + ", companyName: " + companyName + ", industry: " + industry)
            conn2 = util.mysql_connection()
            if conn2 is not None:
                cursor2 = conn2.cursor()
                symbol_already_added_select_query = "select id, symbol from equityStocks where symbol = '" + symbol + "';"
                print("symbol_already_added_select_query: " + symbol_already_added_select_query)
                cursor2.execute(symbol_already_added_select_query)
                print("cursor2.rowcount: " + str(cursor2.rowcount))
                rows = cursor2.fetchall()
                if not rows:
                    conn3 = util.mysql_connection()
                    if conn3 is not None:
                        cursor3 = conn3.cursor()
                        companyName = companyName.replace("'", "")
                        insert_query = None
                        if category == -1:
                            insert_query = "INSERT INTO equityStocks (symbol, companyName, industry) values ('" + symbol + "', '" + companyName + "', '" + industry + "');"
                        else:
                            insert_query = "INSERT INTO equityStocks (symbol, companyName, industry, category) values ('" + symbol + "', '" + companyName + "', '" + industry + "', '" + str(category) + "');"
                        print("insert_query: " + insert_query)
                        cursor3.execute(insert_query)
                        conn3.commit()
                    conn3.close
                conn2.close
        conn1.close


def populate_equity_stocks_with_all_ind_nifty():
    populate_equity_stocks_with_ind_nifty("ind_nifty50list", 5)
    populate_equity_stocks_with_ind_nifty("ind_niftynext50list", 4)
    populate_equity_stocks_with_ind_nifty("ind_nifty100list", -1)
    populate_equity_stocks_with_ind_nifty("ind_nifty200list", 3)
    populate_equity_stocks_with_ind_nifty("ind_nifty500list", 2)
    populate_equity_stocks_with_ind_nifty("ind_nifty500Multicap502525_list", 1)
    populate_equity_stocks_with_ind_nifty("ind_niftymidcap50list", 1)
    populate_equity_stocks_with_ind_nifty("ind_niftymidcap100list", 1)
    populate_equity_stocks_with_ind_nifty("ind_niftymidcap150list", 1)
    populate_equity_stocks_with_ind_nifty("ind_niftysmallcap50list", 1)
    populate_equity_stocks_with_ind_nifty("ind_niftysmallcap100list", 1)
    populate_equity_stocks_with_ind_nifty("ind_niftysmallcap250list", 1)
    populate_equity_stocks_with_ind_nifty("ind_niftymicrocap250_list", 1)
    populate_equity_stocks_with_ind_nifty("ind_niftylargemidcap250list", 1)
    populate_equity_stocks_with_ind_nifty("ind_niftymidsmallcap400list", 1)


def populate_equity_stocks_with_instruments():
    conn1 = util.mysql_connection()
    if conn1 is not None:
        cursor1 = conn1.cursor()
        select_query = "select id, symbol from equityStocks where nseToken is NULL or bseToken is NULL;"
        print(select_query)
        cursor1.execute(select_query)
        for (id, symbol) in cursor1:
            print("id: " + str(id) + ", symbol: " + symbol)
            exchanges = ["NSE", "BSE"]
            conn2 = util.mysql_connection()
            if conn2 is not None:
                cursor2 = conn2.cursor()
                print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                for exchange in exchanges:
                    token_not_added_select_query = "select * from instruments where trading_symbol = '" + symbol + "' and exchange = '" + exchange + "';"
                    print("symbol_already_added_select_query: " + token_not_added_select_query)
                    cursor2.execute(token_not_added_select_query)
                    for (id, instrument_token, trading_symbol, instrument_type, exchange) in cursor2:
                        print("id: " + str(id) + ", instrument_token: " + instrument_token + ", trading_symbol: " + trading_symbol + ", instrument_type: " + instrument_type + ", exchange: " + exchange)
                        conn3 = util.mysql_connection()
                        if conn3 is not None:
                            cursor3 = conn3.cursor()
                            update_query = ""
                            if exchange == 'NSE':
                                update_query = "update equityStocks set nseToken = '" + instrument_token + "' where symbol = '" + symbol + "';"
                            if exchange == 'BSE':
                                update_query = "update equityStocks set bseToken = '" + instrument_token + "' where symbol = '" + symbol + "';"
                            print("update_query: " + update_query)
                            cursor3.execute(update_query)
                            conn3.commit()
                        conn3.close
                print("============================================================================")
            conn2.close
    conn1.close


def delete_temporary_tables():
    conn1 = util.mysql_connection()
    if conn1 is not None:
        cursor1 = conn1.cursor()
        temp_tables = ["ind_nifty100list",
                       "ind_nifty200list",
                       "ind_nifty500Multicap502525_list",
                       "ind_nifty500list",
                       "ind_nifty50list",
                       "ind_niftylargemidcap250list",
                       "ind_niftymicrocap250_list",
                       "ind_niftymidcap100list",
                       "ind_niftymidcap150list",
                       "ind_niftymidcap50list",
                       "ind_niftymidsmallcap400list",
                       "ind_niftynext50list",
                       "ind_niftysmallcap100list",
                       "ind_niftysmallcap250list",
                       "ind_niftysmallcap50list",
                       "instruments"]
        for temp_table in temp_tables:
            drop_temp_able_query = "drop table if exists " + temp_table + ";"
            cursor1.execute(drop_temp_able_query)
    conn1.close


os.system("rm -rf " + master_data_file_dir)
os.system("mkdir " + master_data_file_dir)
download_and_process_master_data_files("ind_nifty")
download_and_process_master_data_files("kite_token")
populate_equity_stocks_with_all_ind_nifty()
populate_equity_stocks_with_instruments()
delete_temporary_tables()
os.system("rm -rf " + master_data_file_dir)
conn = util.mysql_connection()
if conn is not None:
    cursor = conn.cursor()
    cursor.execute("update equityStocks set symbol = 'ADANIGREEN-BE', nseToken = '913665' where symbol = 'ADANIGREEN';")
    cursor.execute("update equityStocks set symbol = 'ADANITRANS-BE', nseToken = '2616577' where symbol = 'ADANITRANS';")
    cursor.execute("update equityStocks set symbol = 'ATGL-BE', nseToken = '1554945' where symbol = 'ATGL';")
    cursor.execute("update equityStocks set symbol = 'AFFLE-BE', nseToken = '2904065' where symbol = 'AFFLE';")
    cursor.execute("update equityStocks set symbol = 'IIFL-BE', nseToken = '3023873' where symbol = 'IIFL';")
    cursor.execute("update equityStocks set symbol = 'SUPPETRO-BE', nseToken = '1696001' where symbol = 'SUPPETRO';")
    cursor.execute("update equityStocks set symbol = 'TANLA-BE', nseToken = '3578881' where symbol = 'TANLA';")
    cursor.execute("update equityStocks set symbol = 'PRAJIND-BE', nseToken = '1262337' where symbol = 'PRAJIND';")
    cursor.execute("update equityStocks set symbol = 'AGCNET-BE', nseToken = '2089985' where symbol = 'AGCNET';")
    cursor.execute("update equityStocks set symbol = 'BORORENEW-BE', nseToken = '807681' where symbol = 'BORORENEW';")
    cursor.execute("update equityStocks set symbol = 'CGPOWER-BE', nseToken = '1258753' where symbol = 'CGPOWER';")
    cursor.execute("update equityStocks set symbol = 'GREENPANEL-BE', nseToken = '3541761' where symbol = 'GREENPANEL';")
    cursor.execute("update equityStocks set symbol = 'HNDFDS-BE', nseToken = '3119361' where symbol = 'HNDFDS';")
    cursor.execute("update equityStocks set symbol = 'JSWISPL-BE', nseToken = '1196289' where symbol = 'JSWISPL';")
    cursor.execute("update equityStocks set symbol = 'MAGMA-BE', nseToken = '2919937' where symbol = 'MAGMA';")
    cursor.execute("update equityStocks set symbol = 'NEULANDLAB-BE', nseToken = '1716993' where symbol = 'NEULANDLAB';")
    cursor.execute("update equityStocks set symbol = 'RTNINDIA-BE', nseToken = '6989057' where symbol = 'RTNINDIA';")
    cursor.execute("update equityStocks set symbol = 'RPOWER-BE', nseToken = '3906817' where symbol = 'RPOWER';")
    cursor.execute("update equityStocks set symbol = 'SHIL-BE', nseToken = '4081921' where symbol = 'SHIL';")
    cursor.execute("update equityStocks set symbol = 'TATASTLLP-BE', nseToken = '2031873' where symbol = 'TATASTLLP';")
    cursor.execute("update equityStocks set symbol = 'TTML-BE', nseToken = '2293249' where symbol = 'TTML';")
    cursor.execute("update equityStocks set symbol = 'TEJASNET-BE', nseToken = '5410561' where symbol = 'TEJASNET';")
    cursor.execute("update equityStocks set symbol = 'KIRLOSBROS-BE', nseToken = '4757505' where symbol = 'KIRLOSBROS';")
    cursor.execute("update equityStocks set symbol = 'PNBHOUSING-BE', nseToken = '4843009' where symbol = 'PNBHOUSING';")
    cursor.execute("update equityStocks set symbol = 'ECLERX-BE-BE', nseToken = '3886849' where symbol = 'ECLERX-BE';")
    cursor.execute("update equityStocks set symbol = 'DEEPAKFERT-BE', nseToken = '1799169' where symbol = 'DEEPAKFERT';")
    cursor.execute("update equityStocks set symbol = 'GDL-BE', nseToken = '3004929' where symbol = 'GDL';")
    cursor.execute("update equityStocks set symbol = 'GPIL-BE', nseToken = '3433473' where symbol = 'GPIL';")
    cursor.execute("update equityStocks set symbol = 'HGS-BE', nseToken = '3767041' where symbol = 'HGS';")
    cursor.execute("update equityStocks set symbol = 'JPASSOCIAT-BE', nseToken = '2934017' where symbol = 'JPASSOCIAT';")
    cursor.execute("update equityStocks set symbol = 'RELINFRA-BE', nseToken = '1226497' where symbol = 'RELINFRA';")
    cursor.execute("update equityStocks set symbol = 'SARDAEN-BE', nseToken = '4547073' where symbol = 'SARDAEN';")
    cursor.execute("update equityStocks set symbol = 'SOMANYCERA-BE', nseToken = '1675265' where symbol = 'SOMANYCERA';")
    conn.commit()
    conn.close
