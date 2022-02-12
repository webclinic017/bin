from kiteconnect import KiteConnect


def get_kite_connect_obj():
    local_data = open('../../connect/base_path/local_data.txt', 'r').read()
    api_key = open(local_data + '/kite_api_key.txt', 'r').read()
    access_token = open(local_data + '/kite_access_token.txt', 'r').read()
    kiteConnectObj = KiteConnect(api_key=api_key)
    kiteConnectObj.set_access_token(access_token)
    return kiteConnectObj
