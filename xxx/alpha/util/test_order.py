import order
import connect

kite = connect.get_kite_connect_obj()
order.place_buy_order(kite, 'AMBUJACEM')
