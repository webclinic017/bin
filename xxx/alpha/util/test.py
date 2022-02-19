# insert_query = "insert into breakout_trendline_1 (stock_symbol, scan_date, utl_left_touching_date, utl_right_touching_date, utl_left_touching_value, utl_right_touching_value, percentage_high_diff_per_day, avg_close, avg_volume, today_utl, today_open, today_close, today_high, today_low, today_volume) values ('" + stock_symbol + "', '" + scan_date + "', '" + utl_left_touching_date + "', '" + utl_right_touching_date + "', '" + str(utl_left_touching_value) + "', '" + "' + str(utl_right_touching_value) + "', '" + str(percentage_high_diff_per_day) + "', '" + str(avg_close) + "', '" + str(avg_volume) + "', '" + str(today_utl) + "', '" + str(today_open) + "', '" + str(today_close) + "', '" + str(today_high) + "', '" + str(today_low) + "', '" + str(today_volume) + "');"
stock_symbol = "XYZ"
scan_date = "2022-02-17"
utl_left_touching_date = "2022-02-17"
utl_right_touching_date = "2022-02-17"
utl_left_touching_value = 15.15
utl_right_touching_value = 16.16
percentage_high_diff_per_day = 0.89
avg_close = 14.0345
avg_volume = 100.9873092
today_utl = 17.001
today_open = 16.5
today_close = 16.8
today_high = 16.9
today_low = 16.45
today_volume = 99
insert_query = "insert into breakout_trendline_1 (stock_symbol, scan_date, utl_left_touching_date, utl_right_touching_date, utl_left_touching_value, utl_right_touching_value, percentage_high_diff_per_day, avg_close, avg_volume, today_utl, today_open, today_close, today_high, today_low, today_volume) values ('" + stock_symbol + "', '" + scan_date + "', '" + utl_left_touching_date + "', '" + utl_right_touching_date + "', '" + str(utl_left_touching_value) + "', '" + str(utl_right_touching_value) + "', '" + str(percentage_high_diff_per_day) + "', '" + str(avg_close) + "', '" + str(avg_volume) + "', '" + str(today_utl) + "', '" + str(today_open) + "', '" + str(today_close) + "', '" + str(today_high) + "', '" + str(today_low) + "', '" + str(today_volume) + "');"
print(insert_query)
