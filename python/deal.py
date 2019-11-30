import pandas as pd
import datetime
from sqlalchemy import create_engine
import json

def get_db_data(time, hour=3):
    host = '127.0.0.1'
    username = 'root'
    password = '123456'
    port = 3307
    database = 'log'
    end = 24 + hour
    engine = create_engine(
        'mysql+pymysql://' + username + ':' + password + '@' + host + ':' + str(port) + '/' + database)
    pre_sql_query = '''
     select date,logdata.count 
     from logdata
     where time >= date_sub(date('%(time)s'),interval %(hour)s hour)
     and time <= date_add(date('%(time)s'),interval %(end)s hour)
     '''
    sql_query = pre_sql_query % {'time': time, 'hour': str(hour), 'end': str(end)}
    df = pd.read_sql_query(sql_query, engine)
    df_dict = {'date': df['date'].tolist(), 'count': df['count'].tolist()}
    return json.dumps(df_dict)


"""
获取前一天后一天的时间
"""


def time_pre_latter(time):
    d = datetime.datetime.strptime(time, '%Y-%m-%d')
    begin = (d + datetime.timedelta(days=-1)).strftime('%Y-%m-%d')
    end = (d + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    return begin, end


def application(env, start_response):
    status = "200 OK"
    headers = [("Content-Type", "application/json;charset=UTF-8")]

    start_response(status, headers)
    return get_db_data(env['data']['time'])
