from kiteconnect import KiteTicker, KiteConnect

if __name__ == '__main__':
    api_key = open('txt/api_key.txt', 'r').read()
    api_secret = open('txt/api_secret.txt', 'r').read()

    kite = KiteConnect(api_key=api_key)

    # print(kite.login_url())
    # https://kite.trade/connect/login?api_key=zrsxqoxccs0zg8na&v=3
    kite_session = kite.generate_session("1bRDhjR1wUzpsMTLcB9WxNQL4YfeDs6d", api_secret=api_secret)
    access_token = kite_session['access_token']

    print(access_token)
    with open('txt/access_token.txt', 'w') as ak:
        ak.write(access_token)
