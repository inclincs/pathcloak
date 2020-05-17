import os



path = tuple(__file__.split(os.sep)[:-2])

source_path = path + ('src',)
data_path = path + ('data',)

database_path = data_path

obu = { 'rx': { 'ip': '', 'port': 9992 }, 'tx': { 'ip': '192.168.0.40', 'port': 9911 } }
server = { 'ip': 'http://pylon.hanyang.ac.kr', 'port': 8181 }

vehicle = obu['tx']['ip'].split('.')[-1]