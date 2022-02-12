import order
from kiteconnect import KiteConnect

local_data = open('../../connect/base_path/local_data.txt', 'r').read()
api_key = open(local_data + '/kite_api_key.txt', 'r').read()
access_token = open(local_data + '/kite_access_token.txt', 'r').read()
kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

order.place_buy_order(kite, 'AMBUJACEM')
