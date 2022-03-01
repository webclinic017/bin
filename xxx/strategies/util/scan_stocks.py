import connect


def get_category_string(category_array):
    category_string = ""
    itr = 0
    for category in category_array:
        category_string = category_string + "category = '" + str(category) + "'"
        itr = itr + 1
        if itr != len(category_array):
            category_string = category_string + " or "
    return category_string


def get_scan_stocks_array(category_array, limit):
    scan_stocks_array = []
    conn = connect.mysql_connection()
    cursor = conn.cursor()
    select_equity_stocks = ""
    if len(category_array) == 0 and limit is None:
        select_equity_stocks = "select id, symbol, category, nseToken from equityStocks;"
    elif len(category_array) == 0 and limit is not None:
        select_equity_stocks = "select id, symbol, category, nseToken from equityStocks limit " + str(limit) + ";"
    elif len(category_array) > 0 and limit is None:
        category_string = get_category_string(category_array)
        select_equity_stocks = "select id, symbol, category, nseToken from equityStocks where " + category_string + ";"
    elif len(category_array) > 0 and limit is not None:
        category_string = get_category_string(category_array)
        select_equity_stocks = "select id, symbol, category, nseToken from equityStocks where " + category_string + " limit " + str(limit) + ";"
    # print("select_equity_stocks: " + select_equity_stocks)
    cursor.execute(select_equity_stocks)
    for (id, symbol, category, nseToken) in cursor:
        stock_detail = []
        stock_detail.append(symbol)
        stock_detail.append(nseToken)
        stock_detail.append(str(category))
        scan_stocks_array.append(stock_detail)
    cursor.close()
    conn.close()
    return scan_stocks_array
