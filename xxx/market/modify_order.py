#!python
import util
import logging
from kiteconnect import KiteConnect

api_key = open(util.baby_0_dir + "txt/api_key.txt", 'r').read()
api_secret = open(util.baby_0_dir + "txt/api_secret.txt", 'r').read()
access_token = open(util.baby_0_dir + "txt/access_token.txt", 'r').read()
kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

stock = 'AMBUJACEM'
ltp = kite.ltp('NSE:' + stock)
price = ltp['NSE:' + stock]['last_price']
print("price: " + str(price))

try:
    order_id = kite.modify_order(variety=kite.VARIETY_REGULAR,
                                 order_id='210625001903344',
                                 price=price - 5
                                )

    print("Order placed. ID is: {}".format(order_id))
except Exception as e:
    # logging.info("Order placement failed: {}".format(e.message))
    print("exception in placing order for the symbol: " + stock)
    print(str(e))
    if str(e).find('Markets are closed right now') != -1:
        print("================================================")
