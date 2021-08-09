# Strategy based on rsi and candle only. If RSI is increasing just above 60,
# decreases for one or two days and again increases above 60, then it can be a signal.

import os
import pandas as pd
from stockstats import StockDataFrame
from datetime import datetime, timedelta
from kiteconnect import KiteConnect

cwd = os.getcwd()
print("cwd: " + cwd)
api_key = open(cwd + "/../txt/api_key.txt", 'r').read()
api_secret = open(cwd + "/../txt/api_secret.txt", 'r').read()
access_token = open(cwd + "/../txt/access_token.txt", 'r').read()

kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

from_date = datetime.strftime(datetime.now() - timedelta(2000), '%Y-%m-%d')
print("from_date: " + from_date)
to_date = datetime.today().strftime('%Y-%m-%d')
print("to_date: " + to_date)

records = kite.historical_data('3861249', from_date=from_date, to_date=to_date, interval='day')
df = pd.DataFrame(records)
for row_index, row in df.iterrows():
    print("date: " + str(row['date']))
    print("open: " + str(row['open']))
    print("high: " + str(row['high']))
    print("low: " + str(row['low']))
    print("close: " + str(row['close']))
    print("volume: " + str(row['volume']))
