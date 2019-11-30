import pymysql
import sqlalchemy
from sqlalchemy import create_engine
import pandas as pd
import sys
import datetime

host = '127.0.0.1'
username = 'root'
password = '123456'
port = 3307
database = 'log'

engine = create_engine('mysql+pymysql://' + username + ':' + password + '@' + host + ':' + str(port) + '/' + database)
sql_query = 'select * from logdata;'
# 使用pandas的read_sql_query函数执行SQL语句，并存入DataFrame
'''
df_read = pd.read_sql_query(sql_query, engine)
print(df_read)
'''
names = ['date', 'info', 'python', 'database', 'process', 'count']
data = pd.read_table("data.log", sep="(\s+-\s+)|(\s+:\s+)", header=None, parse_dates=[0], engine='python')
result_data = data[[0, 3, 6, 9, 12, 15]]
result_data.columns = names

#

f = lambda x: datetime.datetime.strptime(x[0:19], "%m/%d/%Y %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')

result_data['time'] = result_data['date'].map(f)
print(result_data)
result_data.to_sql('logdata', engine, index=False, if_exists='append',
                   dtype={'time': sqlalchemy.types.DATETIME,
                          'info': sqlalchemy.types.String(length=10),
                          'python': sqlalchemy.types.String(length=40),
                          'database': sqlalchemy.types.String(length=10),
                          'process': sqlalchemy.types.String(length=45),
                          'count': sqlalchemy.types.INT,
                          'date': sqlalchemy.types.String(length=45),
                          })
