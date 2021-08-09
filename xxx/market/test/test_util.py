import util
import pandas as pd

df = pd.DataFrame({
    'first_name': ['John', 'Jane', 'Marry', 'Victoria', 'Gabriel', 'Layla'],
    'last_name': ['Smith', 'Doe', 'Jackson', 'Smith', 'Brown', 'Martinez'],
    'open': [22, 22, 23, 25, 26, 27],
    'close': [980, 156, 550, 2200, 75000, 75000],
    'high': [51, 58, 58, 656, 658, 710]},
    index=['id001', 'id002', 'id003', 'id004', 'id005', 'id006'])

# is_high_or_candle_height_continuously_increasing = util.is_high_or_candle_height_continuously_increasing(df, 0, 5)
# print("is_any_attribute_continuously_increasing: " + str(is_high_or_candle_height_continuously_increasing))
util.max_array(df, ['open', 'close'])
