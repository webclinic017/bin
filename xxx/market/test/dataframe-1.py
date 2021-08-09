import util
import pandas as pd

df = pd.DataFrame({
    'first_name': ['John', 'Jane', 'Marry', 'Victoria', 'Gabriel', 'Layla'],
    'last_name': ['Smith', 'Doe', 'Jackson', 'Smith', 'Brown', 'Martinez'],
    'age': [11, 22, 24, 25, 26, 25]},
    index=['id001', 'id002', 'id003', 'id004', 'id005', 'id006'])

# print(df['first_name'])
# print(df.index)
is_continuously_increasing = util.is_continuously_increasing(df['age'], 2, 4)
print("is_continuously_increasing: " + str(is_continuously_increasing))
