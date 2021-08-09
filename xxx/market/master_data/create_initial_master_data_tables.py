import util


conn = util.mysql_connection()
if conn is not None:
    cursor = conn.cursor()
    cursor.execute("drop table if exists master_data_downloads;")
    cursor.execute("create table master_data_downloads (id INT NOT NULL AUTO_INCREMENT, type VARCHAR(255) NOT NULL, "
                   "name VARCHAR(255) NOT NULL, link VARCHAR(1024) NOT NULL, PRIMARY KEY (id));")
    cursor.execute("insert into master_data_downloads (type, name, link) values ('ind_nifty', 'ind_nifty50list.csv', "
                   "'https://www1.nseindia.com/content/indices/ind_nifty50list.csv');")
    cursor.execute("insert into master_data_downloads (type, name, link) values ('ind_nifty', "
                   "'ind_niftynext50list.csv', 'https://www1.nseindia.com/content/indices/ind_niftynext50list.csv');")
    cursor.execute("insert into master_data_downloads (type, name, link) values ('ind_nifty', 'ind_nifty100list.csv', "
                   "'https://www1.nseindia.com/content/indices/ind_nifty100list.csv');")
    cursor.execute("insert into master_data_downloads (type, name, link) values ('ind_nifty', 'ind_nifty200list.csv', "
                   "'https://www1.nseindia.com/content/indices/ind_nifty200list.csv');")
    cursor.execute("insert into master_data_downloads (type, name, link) values ('ind_nifty', 'ind_nifty500list.csv', "
                   "'https://www1.nseindia.com/content/indices/ind_nifty500list.csv');")
    cursor.execute("insert into master_data_downloads (type, name, link) values ('ind_nifty', "
                   "'ind_nifty500Multicap502525_list.csv', "
                   "'https://www1.nseindia.com/content/indices/ind_nifty500Multicap502525_list.csv');")
    cursor.execute("insert into master_data_downloads (type, name, link) values ('ind_nifty', "
                   "'ind_niftymidcap50list.csv', "
                   "'https://www1.nseindia.com/content/indices/ind_niftymidcap50list.csv');")
    cursor.execute("insert into master_data_downloads (type, name, link) values ('ind_nifty', "
                   "'ind_niftymidcap100list.csv', "
                   "'https://www1.nseindia.com/content/indices/ind_niftymidcap100list.csv');")
    cursor.execute("insert into master_data_downloads (type, name, link) values ('ind_nifty', "
                   "'ind_niftymidcap150list.csv', "
                   "'https://www1.nseindia.com/content/indices/ind_niftymidcap150list.csv');")
    cursor.execute("insert into master_data_downloads (type, name, link) values ('ind_nifty', "
                   "'ind_niftysmallcap50list.csv', "
                   "'https://www1.nseindia.com/content/indices/ind_niftysmallcap50list.csv');")
    cursor.execute("insert into master_data_downloads (type, name, link) values ('ind_nifty', "
                   "'ind_niftysmallcap100list.csv', "
                   "'https://www1.nseindia.com/content/indices/ind_niftysmallcap100list.csv');")
    cursor.execute("insert into master_data_downloads (type, name, link) values ('ind_nifty', "
                   "'ind_niftysmallcap250list.csv', "
                   "'https://www1.nseindia.com/content/indices/ind_niftysmallcap250list.csv');")
    cursor.execute("insert into master_data_downloads (type, name, link) values ('ind_nifty', "
                   "'ind_niftymicrocap250_list.csv', "
                   "'https://www1.nseindia.com/content/indices/ind_niftymicrocap250_list.csv');")
    cursor.execute("insert into master_data_downloads (type, name, link) values ('ind_nifty', "
                   "'ind_niftylargemidcap250list.csv', "
                   "'https://www1.nseindia.com/content/indices/ind_niftylargemidcap250list.csv');")
    cursor.execute("insert into master_data_downloads (type, name, link) values ('ind_nifty', "
                   "'ind_niftymidsmallcap400list.csv', "
                   "'https://www1.nseindia.com/content/indices/ind_niftymidsmallcap400list.csv');")
    cursor.execute("insert into master_data_downloads (type, name, link) values ('kite_token', 'instruments', "
                   "'https://api.kite.trade/instruments');")

    show_table_equityStocks = "SHOW TABLES LIKE 'equityStocks';"
    cursor.execute(show_table_equityStocks)
    rows = cursor.fetchall()
    if not rows:
        cursor.execute("CREATE TABLE equityStocks (id INT NOT NULL AUTO_INCREMENT, symbol VARCHAR(255) NOT NULL, "
                   "companyName VARCHAR(255) NOT NULL, industry VARCHAR(255) NOT NULL, category INT NOT NULL DEFAULT "
                   "1, nseToken VARCHAR(255), bseToken VARCHAR(255), PRIMARY KEY (id));")

    conn.commit()
    conn.close
