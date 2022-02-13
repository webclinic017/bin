import connect
import market_days
from datetime import date, datetime, timedelta


def get_scan_dates_array(end_date, previous_number_of_market_days):
    scan_dates_array = []
    number_of_days_to_consider = 0
    if previous_number_of_market_days <= 20:
        number_of_days_to_consider = 30
    elif previous_number_of_market_days <= 1000:
        number_of_days_to_consider = previous_number_of_market_days * 1.7
    else:
        number_of_days_to_consider = 1800
    scan_end_date = date(int(end_date[0:4]), int(end_date[5:7]), int(end_date[8:10]))
    scan_start_date = scan_end_date - timedelta(days=(number_of_days_to_consider - 1))
    num_days = scan_end_date - scan_start_date
    temp_scan_date_array = []
    conn = connect.mysql_connection()
    for i in range(num_days.days + 1):
        if len(temp_scan_date_array) == previous_number_of_market_days:
            break
        day = scan_end_date - timedelta(days=i)
        if market_days.is_a_market_day_with_conn(conn, str(day)):
            temp_scan_date_array.append(str(day))
    for scan_date in reversed(temp_scan_date_array):
        scan_dates_array.append(scan_date)
    conn.close()
    return scan_dates_array
