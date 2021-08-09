#!python
import util
import logging
from kiteconnect import KiteConnect

logging.basicConfig(level=logging.ERROR)

api_key = open(util.baby_0_dir + "txt/api_key.txt", 'r').read()
api_secret = open(util.baby_0_dir + "txt/api_secret.txt", 'r').read()
access_token = open(util.baby_0_dir + "txt/access_token.txt", 'r').read()
kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)


def get_position_price(kite, position_order_id):
    total_quantified_price = 0
    total_quantity = 0
    trades = kite.order_trades(position_order_id)
    for trade in trades:
        this_quantity = trade['quantity']
        this_price = trade['average_price']
        this_quantified_price = this_quantity * this_price
        total_quantified_price += this_quantified_price
        total_quantity += this_quantity
    position_price = total_quantified_price / total_quantity
    return position_price


# Place orders
# stocks = ['AMBUJACEM']
# # stocks = ['KTKBANK', 'EDELWEISS', 'FRETAIL']
# for stock in stocks:
#     ltp = kite.ltp('NSE:' + stock)
#     price = ltp['NSE:' + stock]['last_price']
#     print("price: " + str(price))
#     try:
#         order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
#                                     exchange=kite.EXCHANGE_NSE,
#                                     tradingsymbol=stock,
#                                     transaction_type=kite.TRANSACTION_TYPE_SELL,
#                                     quantity=1,
#                                     product=kite.PRODUCT_MIS,
#                                     order_type=kite.ORDER_TYPE_MARKET,
#                                     # price=price,
#                                     validity='DAY'
#                                     )
#
#         logging.info("Order placed. ID is: {}".format(order_id))
#     except Exception as e:
#         # logging.info("Order placement failed: {}".format(e.message))
#         print("exception in placing order for the symbol: " + stock)
#         print(str(e))
#         if str(e).find('Markets are closed right now') != -1:
#             print("================================================")

# for stock in stocks:
#     ltp = kite.ltp('NSE:' + stock)
#     price = ltp['NSE:' + stock]['last_price']
#     print("price: " + str(price))
#     try:
#         order_id = kite.place_order(variety=kite.VARIETY_CO,
#                                     exchange=kite.EXCHANGE_NSE,
#                                     tradingsymbol=stock,
#                                     transaction_type=kite.TRANSACTION_TYPE_SELL,
#                                     quantity=1,
#                                     product=kite.PRODUCT_MIS,
#                                     order_type=kite.ORDER_TYPE_MARKET,
#                                     trigger_price=price + 1,
#                                     validity='DAY'
#                                     )
#
#         logging.info("Order placed. ID is: {}".format(order_id))
#     except Exception as e:
#         logging.info("Order placement failed: {}".format(e.message))

# for stock in stocks:
#     ltp = kite.ltp('NSE:' + stock)
#     price = ltp['NSE:' + stock]['last_price']
#     print("price: " + str(price))
#     try:
#         order_id = kite.place_order(variety=kite.VARIETY_BO,
#                                     exchange=kite.EXCHANGE_NSE,
#                                     tradingsymbol=stock,
#                                     transaction_type=kite.TRANSACTION_TYPE_BUY,
#                                     quantity=1,
#                                     product=kite.PRODUCT_MIS,
#                                     order_type=kite.ORDER_TYPE_SLM,
#                                     price=price,
#                                     trigger_price=price,
#                                     stoploss=1,
#                                     squareoff=1,
#                                     validity='DAY'
#                                     )
#
#         logging.info("Order placed. ID is: {}".format(order_id))
#     except Exception as e:
#         logging.info("Order placement failed: {}".format(e.message))


# Fetch all orders
# print(kite.order_history('210621004123176'))
# print(kite.order_trades('210621004123176'))
# print(kite.order_trades('210621000446577'))
# print("position_price: " + str(get_position_price(kite, '210621004123176')))
# print("round_off: " + str(round(1.4, 2)))
print(kite.orders())

# # Get instruments
# print(str(kite.instruments()))

# Place an mutual fund order
# kite.place_mf_order(
#     tradingsymbol="INF090I01239",
#     transaction_type=kite.TRANSACTION_TYPE_BUY,
#     amount=5000,
#     tag="mytag"
# )

# Cancel a mutual fund order
# kite.cancel_mf_order(order_id="order_id")

# Get mutual fund instruments
# kite.mf_instruments()