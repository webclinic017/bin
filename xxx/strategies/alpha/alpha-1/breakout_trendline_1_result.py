import sys
sys.path.append('../../util')
import time
import connect

arrays_size = 5

category_array = [2, 3, 4, 5]
avg_volume_array = [None] * arrays_size
vol_mult_array = [None] * arrays_size
percentage_change_per_day_array = [None] * arrays_size
number_of_waiting_days_for_breakout_array = [None] * arrays_size
fractional_upper_wick_size_array = [None] * arrays_size
percentage_diff_between_breakout_close_and_breakout_8MA_array = [None] * arrays_size
percentage_diff_between_breakout_close_and_buying_price_array = [None] * arrays_size
quantity_array = [None] * arrays_size
percentage_diff_between_stoploss_and_buying_price_array = [None] * arrays_size


def all_permutations_of_different_values(array_of_array):
    number_of_arrays = len(array_of_array)
    for i in range(0, len(array_of_array[0]) - 1):
        for j in range(i + 1, len(array_of_array[0])):
            print(str(array_of_array[0][i]) + " - " + str(array_of_array[0][j]))
    itr = 0
    for itr_0 in range(0, len(array_of_array[0])):
        for i in range(0, len(array_of_array[0]) - 1):
            for j in range(i + 1, len(array_of_array[0])):
                print(str(array_of_array[0][i]) + " - " + str(array_of_array[0][j]))
        for itr_1 in range(0, len(array_of_array[1])):
            for itr_2 in range(0, len(array_of_array[2])):
                for itr_3 in range(0, len(array_of_array[3])):
                    for itr_4 in range(0, len(array_of_array[4])):
                        for itr_5 in range(0, len(array_of_array[5])):
                            for itr_6 in range(0, len(array_of_array[6])):
                                for itr_7 in range(0, len(array_of_array[7])):
                                    for itr_8 in range(0, len(array_of_array[8])):
                                        for itr_9 in range(0, len(array_of_array[9])):
                                            # itr = itr + 1
                                            print("itr_0: " + str(itr_0) + ", itr_1: " + str(itr_1) + ", itr_2: " + str(itr_2) + ", itr_3: " + str(itr_3) + ", itr_4: " + str(itr_4) + ", itr_5: " + str(itr_5) + ", itr_6: " + str(itr_6) + ", itr_7: " + str(itr_7) + ", itr_8: " + str(itr_8) + ", itr_9: " + str(itr_9))
    # print("itr: " + str(itr))
    # for i in range(0, number_of_arrays):
    #     for j in range(0, len(array_of_array[i]) - 1):
    #         for k in range(j + 1, len(array_of_array[i])):
    #             print(str(array_of_array[i][j]) + " - " + str(array_of_array[i][k]))


def initialize_min_and_max_element(arr, val):
    arr[0] = arr[len(arr) - 1] = val


def adjust_min_and_max_element(arr, val):
    if val < arr[0]:
        arr[0] = val
    if val > arr[len(arr) - 1]:
        arr[len(arr) - 1] = val


def populate_all_elements_of_array(arr):
    min_val = arr[0]
    max_val = arr[len(arr) - 1]
    diff_val = max_val - min_val
    divisor = len(arr) - 1
    unit_divisor = diff_val / divisor
    for i in range(1, len(arr) - 1, 1):
        arr[i] = min_val + i * unit_divisor


conn1 = connect.mysql_connection()
cursor1 = conn1.cursor()

select_query = "select e.category as category, d.stock_symbol as symbol, d.scan_date as date, d.avg_volume as avg_vol, d.volume_multiplier as vol_mult, d.percentage_change_per_day as '%d/day', d.wait_days_for_breakout as nowd, d.upper_wick_size as wick, b.buying_8MA as b8, d.today_close as close, ((d.today_close- b.buying_8MA) * 100/d.today_close) as '%d_close_b8', ((b.buying_price - d.today_close) * 100/d.today_close) as '%d_close_buy', b.quantity as quantity, b.stoploss as stoploss, ((b.buying_price - b.stoploss) * 100 / b.stoploss) as '%d_stoploss_buy', b.buying_date as bd, b.buying_price as bp, b.selling_date sd, b.selling_price as sp, b.percentage_profit_loss as '%pl', b.waiting_period as wfs from equityStocks e, bkp_breakout_trendline_1_details d, bkp_breakout_trendline_1_backtest b where d.stock_symbol = e.symbol and d.stock_symbol = b.stock_symbol and d.scan_date = b.scan_date and b.should_be_bought = 1;"
cursor1.execute(select_query)
itr = 0
for (
            category,
            symbol,
            date,
            avg_vol,
            vol_mult,
            percentage_change_per_day,
            number_of_waiting_days_for_breakout,
            fractional_upper_wick_size,
            breakout_8MA,
            breakout_close,
            percentage_diff_between_breakout_close_and_breakout_8MA,
            percentage_diff_between_breakout_close_and_buying_price,
            quantity,
            stoploss,
            percentage_diff_between_stoploss_and_buying_price,
            buying_date,
            buying_price,
            selling_date,
            selling_price,
            percentage_profit_loss,
            number_of_waiting_days_for_sell
) in cursor1:
    if itr == 0:
        initialize_min_and_max_element(avg_volume_array, avg_vol)
        initialize_min_and_max_element(vol_mult_array, vol_mult)
        initialize_min_and_max_element(percentage_change_per_day_array, percentage_change_per_day)
        initialize_min_and_max_element(number_of_waiting_days_for_breakout_array, number_of_waiting_days_for_breakout)
        initialize_min_and_max_element(fractional_upper_wick_size_array, fractional_upper_wick_size)
        initialize_min_and_max_element(percentage_diff_between_breakout_close_and_breakout_8MA_array, percentage_diff_between_breakout_close_and_breakout_8MA)
        initialize_min_and_max_element(percentage_diff_between_breakout_close_and_buying_price_array, percentage_diff_between_breakout_close_and_buying_price)
        initialize_min_and_max_element(quantity_array, quantity)
        initialize_min_and_max_element(percentage_diff_between_stoploss_and_buying_price_array, percentage_diff_between_stoploss_and_buying_price)
    else:
        adjust_min_and_max_element(avg_volume_array, avg_vol)
        adjust_min_and_max_element(vol_mult_array, vol_mult)
        adjust_min_and_max_element(percentage_change_per_day_array, percentage_change_per_day)
        adjust_min_and_max_element(number_of_waiting_days_for_breakout_array, number_of_waiting_days_for_breakout)
        adjust_min_and_max_element(fractional_upper_wick_size_array, fractional_upper_wick_size)
        adjust_min_and_max_element(percentage_diff_between_breakout_close_and_breakout_8MA_array, percentage_diff_between_breakout_close_and_breakout_8MA)
        adjust_min_and_max_element(percentage_diff_between_breakout_close_and_buying_price_array, percentage_diff_between_breakout_close_and_buying_price)
        adjust_min_and_max_element(quantity_array, quantity)
        adjust_min_and_max_element(percentage_diff_between_stoploss_and_buying_price_array, percentage_diff_between_stoploss_and_buying_price)
    itr = itr + 1

cursor1.close()
conn1.close()

populate_all_elements_of_array(avg_volume_array)
populate_all_elements_of_array(vol_mult_array)
populate_all_elements_of_array(percentage_change_per_day_array)
populate_all_elements_of_array(number_of_waiting_days_for_breakout_array)
populate_all_elements_of_array(fractional_upper_wick_size_array)
populate_all_elements_of_array(percentage_diff_between_breakout_close_and_breakout_8MA_array)
populate_all_elements_of_array(percentage_diff_between_breakout_close_and_buying_price_array)
populate_all_elements_of_array(quantity_array)
populate_all_elements_of_array(percentage_diff_between_stoploss_and_buying_price_array)

print(avg_volume_array)
print(vol_mult_array)
print(percentage_change_per_day_array)
print(number_of_waiting_days_for_breakout_array)
print(fractional_upper_wick_size_array)
print(percentage_diff_between_breakout_close_and_breakout_8MA_array)
print(percentage_diff_between_breakout_close_and_buying_price_array)
print(quantity_array)
print(percentage_diff_between_stoploss_and_buying_price_array)

array_of_all_arrays = []
array_of_all_arrays.append(category_array)
array_of_all_arrays.append(avg_volume_array)
array_of_all_arrays.append(vol_mult_array)
array_of_all_arrays.append(percentage_change_per_day_array)
array_of_all_arrays.append(number_of_waiting_days_for_breakout_array)
array_of_all_arrays.append(fractional_upper_wick_size_array)
array_of_all_arrays.append(percentage_diff_between_breakout_close_and_breakout_8MA_array)
array_of_all_arrays.append(percentage_diff_between_breakout_close_and_buying_price_array)
array_of_all_arrays.append(quantity_array)
array_of_all_arrays.append(percentage_diff_between_stoploss_and_buying_price_array)

start_time = time.time()
all_permutations_of_different_values(array_of_all_arrays)
end_time = time.time()
time_elapsed = end_time - start_time
print("time_elapsed: " + str(time_elapsed))
