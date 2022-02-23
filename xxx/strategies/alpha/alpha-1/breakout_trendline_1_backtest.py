from datetime import date, datetime, timedelta
from stockstats import StockDataFrame
import pandas as pd
import sys
sys.path.append('../../util')
import connect
import market_days
import strategy_constant

kite = connect.get_kite_connect_obj()
today_date = datetime.today().strftime('%Y-%m-%d')


def is_already_backtested(cursor, stock_symbol, scan_date):
    select_query = "select * from breakout_trendline_1_backtest where scan_date = '" + scan_date + "' and stock_symbol = '" + stock_symbol + "';"
    cursor.execute(select_query)
    rows = cursor.fetchall()
    if not rows:
        return False
    return True


def backtest(conn, stock_symbol, scan_date):
    cursor = conn.cursor()
    select_query = "select symbol, nseToken, category from equityStocks where symbol = '" + stock_symbol + "';"
    cursor.execute(select_query)
    nse_token = ''
    stock_category = -1
    for (symbol, nseToken, category) in cursor:
        nse_token = nseToken
        stock_category = category
    scan_date_day = date(int(scan_date[0:4]), int(scan_date[5:7]), int(scan_date[8:10]))
    print()
    print()
    print("stock_symbol: " + stock_symbol)
    print("scan_date_day: " + str(scan_date_day))
    next_market_day_after_breakout = market_days.next_market_day_without_conn(scan_date)
    scan_date_day_minus_hundred = scan_date_day - timedelta(days=100)
    print("scan_date_day_minus_hundred: " + str(scan_date_day_minus_hundred))
    print("today_date: " + today_date)
    next_of_scan_date_day_minus_hundred = market_days.next_market_day_without_conn(str(scan_date_day_minus_hundred))
    prev_of_today_date = market_days.prev_market_day_without_conn(today_date)
    records = kite.historical_data(nse_token, scan_date_day_minus_hundred, today_date, 'day')
    df = pd.DataFrame(records)
    sdf = StockDataFrame.retype(df)
    print(sdf)
    first_sdf_date = str(sdf.index[0])[0:10]
    last_sdf_date = str(sdf.index[sdf.index.size - 1])[0:10]
    print("next_market_day_after_breakout: " + next_market_day_after_breakout)
    sdf_close_8_sma = sdf['close_8_sma']
    sdf_open = sdf['open']
    sdf_close = sdf['close']
    sdf_low = sdf['low']
    start_itr = -1
    for itr in range(0, sdf.index.size):
        itr_date = str(sdf.index[itr])[0:10]
        if itr_date == next_market_day_after_breakout:
            start_itr = itr
    print(sdf.index[start_itr])
    breakout_itr = start_itr - 1
    breakout_opening_price = sdf_open[breakout_itr]
    breakout_closing_price = sdf_close[breakout_itr]
    breakout_price_change = breakout_closing_price - breakout_opening_price
    min_allowed_buying_price_breakout_wise = breakout_closing_price - breakout_price_change * strategy_constant.allowed_fraction_for_buying
    print("min_allowed_buying_price_breakout_wise: " + str(min_allowed_buying_price_breakout_wise))
    buying_8MA = sdf_close_8_sma[breakout_itr] # closing 8MA of previous day
    print("buying_8MA: " + str(buying_8MA))
    stoploss = max(min_allowed_buying_price_breakout_wise, buying_8MA)
    initial_stoploss = stoploss
    print("initial_stoploss: " + str(stoploss))
    should_be_bought = True
    if next_of_scan_date_day_minus_hundred != first_sdf_date and prev_of_today_date != last_sdf_date:
        should_be_bought = False
    print("sdf_open[start_itr]: " + str(sdf_open[start_itr]))
    if sdf_open[start_itr] < stoploss:
        should_be_bought = False
    buying_date = str(sdf.index[start_itr])[0:10]
    print("buying_date: " + buying_date)
    buying_price = sdf_open[start_itr]
    quantity = int(strategy_constant.amount_for_buying_one_stock / buying_price)
    selling_date = ''
    selling_8MA = -1
    selling_price = -1
    profit_loss = -1
    adjusted_profit_loss = -1
    percentage_profit_loss = - 1
    buying_day = None
    selling_day = None
    selling_buying_days_diff = -1
    print("start_itr: " + str(start_itr))
    print("sdf.index.size: " + str(sdf.index.size))
    for itr in range(start_itr, sdf.index.size):
        if sdf_low[itr] < stoploss:
            selling_date = str(sdf.index[itr])[0:10]
            selling_8MA = sdf_close_8_sma[itr]
            selling_price = stoploss
            break
        else:
            stoploss = max(stoploss, sdf_close_8_sma[itr])
    if selling_date == '':
        should_be_bought = False
    else:
        profit_loss = (selling_price - buying_price) * quantity
        adjusted_profit_loss = -1
        if profit_loss > 0:
            adjusted_profit_loss = profit_loss + (profit_loss / 10)
        if profit_loss < 0:
            adjusted_profit_loss = profit_loss - (profit_loss / 10)
        percentage_profit_loss = adjusted_profit_loss * 100 / (buying_price * quantity)
        buying_day = date(int(buying_date[0:4]), int(buying_date[5:7]), int(buying_date[8:10]))
        selling_day = date(int(selling_date[0:4]), int(selling_date[5:7]), int(selling_date[8:10]))
        selling_buying_days_diff = (selling_day - buying_day).days + 1
        print("selling_buying_diff: " + str(selling_buying_days_diff))
    insert_query = ""
    if not should_be_bought:
        insert_query = "insert into breakout_trendline_1_backtest (stock_category, stock_symbol, scan_date, should_be_bought) values ('" + str(stock_category) + "', '" + stock_symbol + "', '" + scan_date + "', '" + "0" + "');"
    else:
        insert_query = "insert into breakout_trendline_1_backtest (stock_category, stock_symbol, scan_date, should_be_bought, buying_date, buying_8MA, buying_price, quantity, stoploss, selling_date, selling_8MA, selling_price, profit_loss, percentage_profit_loss, waiting_period, percentage_profit_loss_per_day) values ('" + str(stock_category) + "', '" + stock_symbol + "', '" + scan_date + "', '" + "1" + "', '" + buying_date + "', '" + str(buying_8MA) + "', '" + str(buying_price) + "', '" + str(quantity) + "', '" + str(initial_stoploss) + "', '" + selling_date + "', '" + str(selling_8MA) + "', '" + str(selling_price) + "', '" + str(profit_loss) + "', '" + str(percentage_profit_loss) + "', '" + str(selling_buying_days_diff) + "', '" + str(round((percentage_profit_loss / selling_buying_days_diff), 2)) + "');"
    cursor.execute(insert_query)
    cursor.close()
    conn.commit()


end_date = datetime.today().strftime('%Y-%m-%d')

scan_end_date = date(int(end_date[0:4]), int(end_date[5:7]), int(end_date[8:10]))
scan_start_date = scan_end_date - timedelta(days=(365 * 5))
num_days = scan_end_date - scan_start_date
print("scan_end_date: " + str(scan_end_date))
print("scan_start_date: " + str(scan_start_date))
print("num_days: " + str(num_days.days))
conn1 = connect.mysql_connection()
cursor1 = conn1.cursor()
conn2 = connect.mysql_connection()
cursor2 = conn2.cursor()
conn3 = connect.mysql_connection()
for i in range(0, num_days.days + 1, 1):
    scan_date = scan_end_date - timedelta(days=i)
    select_query = "select stock_symbol, scan_date from breakout_trendline_1_details where scan_date = '" + str(scan_date) + "';"
    print(select_query)
    cursor1.execute(select_query)
    found = False
    for (stock_symbol, scan_date) in cursor1:
        already_backtested = is_already_backtested(cursor2, stock_symbol, scan_date)
        if not already_backtested:
            backtest(conn3, stock_symbol, scan_date)
    #         if scan_date == '2021-12-28':
    #             found = True
    #             break
    # if found:
    #     break
conn3.close()
cursor2.close()
conn2.close()
cursor1.close()
conn1.close()
