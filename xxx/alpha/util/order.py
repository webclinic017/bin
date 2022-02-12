#!python
import logging

logging.basicConfig(level=logging.ERROR)


def place_buy_order(kite, stock):
    ltp = kite.ltp('NSE:' + stock)
    price = ltp['NSE:' + stock]['last_price']
    print("price of stock " + stock + ": " + str(price))
    try:
        order_id = kite.place_order(variety=kite.VARIETY_BO,
                                    exchange=kite.EXCHANGE_NSE,
                                    tradingsymbol=stock,
                                    transaction_type=kite.TRANSACTION_TYPE_BUY,
                                    quantity=1,
                                    product=kite.PRODUCT_MIS,
                                    order_type=kite.ORDER_TYPE_SLM,
                                    price=price,
                                    trigger_price=price,
                                    stoploss=1,
                                    squareoff=1,
                                    validity='DAY'
                                    )

        logging.info("Order placed. ID is: {}".format(order_id))
    except Exception as e:
        logging.info("Order placement failed: {}".format(e.message))


def place_sell_order(kite, stock):
    ltp = kite.ltp('NSE:' + stock)
    price = ltp['NSE:' + stock]['last_price']
    print("price of stock " + stock + ": " + str(price))
    try:
        order_id = kite.place_order(variety=kite.VARIETY_BO,
                                    exchange=kite.EXCHANGE_NSE,
                                    tradingsymbol=stock,
                                    transaction_type=kite.TRANSACTION_TYPE_SELL,
                                    quantity=1,
                                    product=kite.PRODUCT_MIS,
                                    order_type=kite.ORDER_TYPE_SLM,
                                    price=price,
                                    trigger_price=price,
                                    stoploss=1,
                                    squareoff=1,
                                    validity='DAY'
                                    )

        logging.info("Order placed. ID is: {}".format(order_id))
    except Exception as e:
        logging.info("Order placement failed: {}".format(e.message))
