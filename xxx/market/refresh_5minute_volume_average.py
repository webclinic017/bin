import util


def update_5minute_data_volume_avg():
    conn1 = util.mysql_connection()
    conn2 = util.mysql_connection()
    conn3 = util.mysql_connection()
    if conn1 and conn2 and conn3 is not None:
        cursor1 = conn1.cursor()
        cursor2 = conn2.cursor()
        cursor3 = conn3.cursor()
        select_equity_stocks = "select id, symbol, industry, category, nseToken from equityStocks where nseToken is not NULL;"
        # select_equity_stocks = "select id, symbol, industry, category, nseToken from equityStocks where nseToken is not NULL and symbol = 'WSTCSTPAPR';"
        cursor1.execute(select_equity_stocks)
        for (id, symbol, industry, category, nseToken) in cursor1:
            fetch_all_5minutes_time = "select symbol, time from 5minute_data where symbol = 'RELIANCE' and date = '2021-04-01';"
            cursor2.execute(fetch_all_5minutes_time)
            for (symbol_val, time_val) in cursor2:
                symbol_details_array = []
                volume_sum = 0
                symbol_volume_query = "select date, volume from 5minute_data where nseToken = '" + nseToken + "' and time = '" + time_val + "';"
                cursor3.execute(symbol_volume_query)
                for (date, volume) in cursor3:
                    volume_sum += volume
                    symbol_details = {'date' : date, 'volume' : volume}
                    symbol_details_array.append(symbol_details)
                volume_avg = int(volume_sum / len(symbol_details_array))
                later_half_length = int(len(symbol_details_array) / 2)
                later_half_sum = 0
                number_of_later_half_days = 0
                for idx in range(later_half_length - 1, len(symbol_details_array)):
                    number_of_later_half_days += 1
                    later_half_sum += symbol_details_array[idx]['volume']
                later_half_avg = (later_half_sum / number_of_later_half_days)
                select_volume_avg_query = "select volume_avg from 5minute_data_volume_avg where nseToken = '" + nseToken + "' and time = '" + time_val + "';"
                cursor3.execute(select_volume_avg_query)
                count_row = cursor3.fetchone()
                volume_avg_query = ''
                if count_row is not None:
                    volume_avg_query = "update 5minute_data_volume_avg set volume_avg = '" + str(volume_avg) + "', later_half_volume_avg = '" + str(later_half_avg) + "' where nseToken = '" + nseToken + "' and time = '" + time_val + "';"
                else:
                    volume_avg_query = "insert into 5minute_data_volume_avg values ('" + nseToken + "', '" + symbol + "', '" + time_val + "', '" + str(volume_avg) + "', '" + str(later_half_avg) + "');"
                cursor3.execute(volume_avg_query)
                conn3.commit()
    conn3.close
    conn2.close
    conn1.close


update_5minute_data_volume_avg()
