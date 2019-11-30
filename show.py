# coding:utf-8
import pandas as pd
import socket
import datetime
from sqlalchemy import create_engine
from multiprocessing import Process

"""
连接数据库获取数据
"""


def get_db_data(time, hour=3):
    host = '127.0.0.1'
    username = 'root'
    password = '123456'
    port = 3307
    database = 'log'
    end = 24 + hour
    engine = create_engine('mysql+pymysql://' + username + ':' + password + '@' + host + ':' + str(port) + '/' + database)
    pre_sql_query = '''
    select date,logdata.count 
    from logdata
    where time >= date_sub(date('%(time)s'),interval %(hour)s hour)
    and time <= date_add(date('%(time)s'),interval %(end)s hour)
    '''
    sql_query = pre_sql_query % {'time': time, 'hour': str(hour), 'end': str(end)}
    return pd.read_sql_query(sql_query, engine)

"""
获取前一天后一天的时间
"""


def time_pre_latter(time):
    d = datetime.datetime.strptime(time, '%Y-%m-%d')
    begin = (d + datetime.timedelta(days=-1)).strftime('%Y-%m-%d')
    end = (d + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    return begin, end

def handle_client(client_socket):
    """
    处理客户端请求
    """
    time = '2019-10-11'

    request_data = client_socket.recv(1024)
    request_lines = request_data.splitlines()
    if request_lines is not None and len(request_lines) > 0:
        result = get_db_data(time)
        request_start_line = request_lines[0].decode('utf-8')
        params = request_start_line.split(' ')
        if params[0].upper() == 'GET':
            if params[1].find('?user_date=') != -1:
                time = params[1].split('=')[1]
                result = get_db_data(time)
    else:
        return
    # 计算前一天后一天
    previous, latter = time_pre_latter(time)
    # 构造响应数据
    response_start_line = "HTTP/1.1 200 OK\r\n"
    response_headers = "Server: My server\r\n"
    response_body = '''
    <!DOCTYPE html>
    <html>
      <head>
      <meta charset="UTF-8">
      <title>数据展示</title>
      <link rel="icon" href="data:;base64,=">
      <script src="https://cdnjs.cloudflare.com/ajax/libs/echarts/4.3.0/echarts-en.min.js"></script>                                                                                                    
      </head>

        <body>
           <h2>''' + time + '''</h2>
           <div  style="width:400px;margin:10px auto" >
           <form  method="get">
            请选择日期: <input type="date" name="user_date" value="''' + time + '''"/>
            <input type="submit" />
           </form>
           </div>
           <div id="main" style="width: 1200px;height:400px;margin:0 auto"></div>
            <div  style="width:250px;margin:0 auto" > 
            <a href="?user_date=''' + previous + '''"> <button >前一天</button></a>
            <a href="?user_date=''' + latter + '''"> <button>后一天</button></a>
            </div>
               <script type="text/javascript">
    
        // 基于准备好的dom，初始化echarts实例
        var myChart = echarts.init(document.getElementById('main'));

        // 指定图表的配置项和数据
        var option = {
          tooltip: {
          show:true,
          trigger: 'axis',
          },
        xAxis: {
          name: "日期",
          nameLocation: "end",
          data:''' + str(result['date'].tolist()) + ''',
          type: "category",
        },
        yAxis: {
          type: "value",
          name: "数量"
        },
        series: [
          {
            data: ''' + str(result['count'].tolist()) + ''',
            type: "line"
          }
        ]
        };

        // 使用刚指定的配置项和数据显示图表。
        myChart.setOption(option);
        
    </script>
        </body>                         
    </html> 
    '''
    response = response_start_line + response_headers + "\r\n" + response_body

    # 向客户端返回响应数据
    client_socket.send(bytes(response, "utf-8"))

    # 关闭客户端连接
    client_socket.close()


if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("", 8000))
    server_socket.listen(128)

    while True:
        client_socket, client_address = server_socket.accept()
        print("[%s, %s]用户连接上了" % client_address)
        handle_client_process = Process(target=handle_client, args=(client_socket,))
        handle_client_process.start()
        client_socket.close()

    # handle_file()
