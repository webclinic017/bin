import connect
from datetime import date, datetime, timedelta
import pandas as pd
from stockstats import StockDataFrame

kite = connect.get_kite_connect_obj()
local_data = open('../../connect/base_path/local_data.txt', 'r').read()

to_date = datetime.today().strftime('%Y-%m-%d')
data_end_date = date(int(to_date[0:4]), int(to_date[5:7]), int(to_date[8:10]))
data_start_date = data_end_date - timedelta(days=365)
from_date = str(data_start_date)
print("from_date: " + from_date)
print("to_date: " + to_date)
records = kite.historical_data('3861249', from_date, to_date, 'day')
df = pd.DataFrame(records)
sdf = StockDataFrame.retype(df)
print(sdf)
