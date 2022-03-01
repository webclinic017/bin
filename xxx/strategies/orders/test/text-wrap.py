import textwrap
import sys
sys.path.append('../../util')
import connect
import logging

kite = connect.get_kite_connect_obj()
logging.basicConfig(level=logging.ERROR)

value = str(kite.instruments(exchange='NSE'))

# Wrap this text.
wrapper = textwrap.TextWrapper(width=80)

word_list = wrapper.wrap(text=value)

# Print each line.
for element in word_list:
    print(element)