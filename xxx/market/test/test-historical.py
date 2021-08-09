import util
from kiteconnect import KiteConnect
from datetime import datetime, timedelta

api_key = open(util.baby_0_dir + "txt/api_key.txt", 'r').read()
api_secret = open(util.baby_0_dir + "txt/api_secret.txt", 'r').read()
access_token = open(util.baby_0_dir + "txt/access_token.txt", 'r').read()
kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)
from_date = datetime.strftime(datetime.now() - timedelta(3000), '%Y-%m-%d')
# print("from_date: " + from_date)
to_date = datetime.today().strftime('%Y-%m-%d')
# print("to_date: " + to_date)
remainder = 1 % 2
print("remainder: " + str(remainder))
kite.historical_data('738561', from_date, to_date, '60minute')
