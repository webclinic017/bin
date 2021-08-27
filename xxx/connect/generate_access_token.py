from kiteconnect import KiteTicker, KiteConnect

local_data = open('../connect/base_path/local_data.txt', 'r').read()

if __name__ == '__main__':
    api_key = open(local_data + '/kite_api_key.txt', 'r').read()
    api_secret = open(local_data + '/kite_api_secret.txt', 'r').read()
    request_token = open(local_data + '/kite_request_token.txt', 'r').read()

    kite = KiteConnect(api_key=api_key)

    # print(kite.login_url())
    # https://kite.trade/connect/login?api_key=zrsxqoxccs0zg8na&v=3
    kite_session = kite.generate_session(request_token, api_secret=api_secret)
    access_token = kite_session['access_token']

    print(access_token)
    with open('base_path/access_token.txt', 'w') as ak:
        ak.write(access_token)
