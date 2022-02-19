import time
import strategy_constant
from datetime import date, datetime, timedelta


def populate_job_array(scan_dates_array, scan_stocks_array, job_details_array):
    for scan_date in scan_dates_array:
        for scan_stock in scan_stocks_array:
            job = {
                "scan_date": scan_date,
                "symbol": scan_stock[0],
                "nse_token": scan_stock[1]
            }
            job_details_array.append(job)


def populate_job_array_and_lot_index_array(scan_dates_array, scan_stocks_array):
    job_details_array = []
    lot_index_details_array = []
    populate_job_array(scan_dates_array, scan_stocks_array, job_details_array)
    total_number_of_jobs = len(job_details_array)
    number_of_lots = int(total_number_of_jobs / strategy_constant.number_of_jobs_in_one_lot)
    for lot_num in range(0, number_of_lots, 1):
        lot_index_details = {
            "lot_min_index" : strategy_constant.number_of_jobs_in_one_lot * lot_num,
            "lot_max_index" : (strategy_constant.number_of_jobs_in_one_lot * (lot_num + 1)) - 1
        }
        lot_index_details_array.append(lot_index_details)
    jobs_in_last_lot = total_number_of_jobs % strategy_constant.number_of_jobs_in_one_lot
    if jobs_in_last_lot > 0:
        lot_index_details = {
            "lot_min_index" : strategy_constant.number_of_jobs_in_one_lot * number_of_lots,
            "lot_max_index" : total_number_of_jobs - 1
        }
        lot_index_details_array.append(lot_index_details)
    return {"job_details_array" : job_details_array, "lot_index_details_array" : lot_index_details_array}


def populate_historical_data_thread_and_method_parameters_array(
        kite,
        thread,
        job_details_array,
        job_details_itr,
        historical_data_thread_array,
        method_parameters_array
):
    scan_date = job_details_array[job_details_itr]['scan_date']
    symbol = job_details_array[job_details_itr]['symbol']
    nse_token = job_details_array[job_details_itr]['nse_token']

    data_end_date = date(int(scan_date[0:4]), int(scan_date[5:7]), int(scan_date[8:10]))
    data_start_date = data_end_date - timedelta(days=(strategy_constant.number_of_days_prev_data_required - 1))

    method_parameters = {
        "symbol": symbol,
        "nse_token": nse_token,
        "data_start_date": str(data_start_date),
        "data_end_date": str(data_end_date)
    }
    method_parameters_array.append(method_parameters)
    historical_data_thread = thread.ThreadWithReturnValue(target=kite.historical_data, args=(
    nse_token, str(data_start_date), str(data_end_date), 'day'))
    historical_data_thread.start()
    historical_data_thread_array.append(historical_data_thread)
    time.sleep(0.30)
