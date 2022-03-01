import sys
sys.path.append('../../util')
import connect
import logging

kite = connect.get_kite_connect_obj()
logging.basicConfig(level=logging.ERROR)


def buy_order():
    stock = 'ADANIPORTS'
    ltp = kite.ltp('NSE:' + stock)
    price = ltp['NSE:' + stock]['last_price']
    print("price: " + str(price))
    try:
        order_id = kite.place_order(variety=kite.VARIETY_CO,
                                    exchange=kite.EXCHANGE_NSE,
                                    tradingsymbol=stock,
                                    transaction_type=kite.TRANSACTION_TYPE_BUY,
                                    quantity=1,
                                    product=kite.PRODUCT_CNC,
                                    order_type=kite.ORDER_TYPE_MARKET,
                                    # price=price,
                                    validity='DAY'
                                    )
        print("Order placed. ID is: {}".format(order_id))
        # logging.info("Order placed. ID is: {}".format(order_id))
    except Exception as e:
        # logging.info("Order placement failed: {}".format(e.message))
        print("exception in placing order for the symbol: " + stock)
        print(str(e))
        if str(e).find('Markets are closed right now') != -1:
            print("================================================")


def sell_order():
    stock = 'ADANIPORTS'
    ltp = kite.ltp('NSE:' + stock)
    price = ltp['NSE:' + stock]['last_price']
    print("price: " + str(price))
    try:
        order_id = kite.place_order(variety=kite.VARIETY_CO,
                                    exchange=kite.EXCHANGE_NSE,
                                    tradingsymbol=stock,
                                    transaction_type=kite.TRANSACTION_TYPE_SELL,
                                    quantity=1,
                                    product=kite.PRODUCT_CNC,
                                    order_type=kite.ORDER_TYPE_SLM,
                                    # price=(price - 5),
                                    trigger_price=(price - 4),
                                    # stoploss=6,
                                    # squareoff=2,
                                    validity='DAY'
                                    )
        print("Order placed. ID is: {}".format(order_id))
        # logging.info("Order placed. ID is: {}".format(order_id))
    except Exception as e:
        # logging.info("Order placement failed: {}".format(e.message))
        print("exception in placing order for the symbol: " + stock)
        print(str(e))
        if str(e).find('Markets are closed right now') != -1:
            print("================================================")


def main():
    # print(format(kite.instruments()))
    # print(str(kite.orders()))
    buy_order()
    sell_order()


if __name__ == "__main__":
    main()
