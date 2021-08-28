import sys, getopt
from kiteconnect import KiteTicker, KiteConnect

local_data = open('../connect/base_path/local_data.txt', 'r').read()

def main(argv):
    request_token = ''
    try:
        opts, args = getopt.getopt(argv,"h:r:",["request_token="])
    except getopt.GetoptError:
        print("exception occurred")
        print('generate_access_token.py -r <request_token>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('generate_access_token.py -r <request_token>')
            sys.exit()
        elif opt in ("-r", "--request_token"):
            request_token = arg

    if request_token == '':
        print("request token required..")
        print('generate_access_token.py -rt <request_token>')
        sys.exit(2)

    api_key = open(local_data + '/kite_api_key.txt', 'r').read()
    api_secret = open(local_data + '/kite_api_secret.txt', 'r').read()

    kite = KiteConnect(api_key=api_key)

    # print(kite.login_url())
    # https://kite.trade/connect/login?api_key=zrsxqoxccs0zg8na&v=3
    kite_session = kite.generate_session(request_token, api_secret=api_secret)
    access_token = kite_session['access_token']

    print(access_token)
    with open(local_data + '/kite_access_token.txt', 'w') as ak:
        ak.write(access_token)

if __name__ == '__main__':
   main(sys.argv[1:])
