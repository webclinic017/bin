from kiteconnect import KiteTicker, KiteConnect
local_data = open('../connect/base_path/local_data.txt', 'r').read()
xxx = open('../connect/base_path/xxx.txt', 'r').read()

if __name__ == '__main__':
    print('local_data: ' + local_data)
    print('xxx: ' + xxx)
