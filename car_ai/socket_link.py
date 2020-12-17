# 导入 socket 模块
import socket
import threading
import time
# 创建socket对象

class socket_server:
    _socket = None
    _connect = None
    _get_data_call_back = None

    def check_recv(self):
        count = 0
        while True:
            print("before")
            try:
                data = self._connect.recv(1024)
            except BlockingIOError as e:
                data = None
            print("after")
            if data:
               if self._get_data_call_back:
                   self._get_data_call_back(data) 
            time.sleep(0.01)
            count += 1

    def __init__(self):
        print("__init")
        self._socket = socket.socket()
        self._socket.bind(('127.0.0.1', 30000))

    def start_listener(self):
        self._socket.listen()
        self._connect, addr = self._socket.accept()
        self._connect.settimeout(0)
        print(self._connect)
        print('连接地址：', addr)

    def start_receive(self):
        thread = threading.Thread(target=self.check_recv)
        thread.run()

    def set_receive_data_call_back(self,call):
        self._get_data_call_back = call

server = socket_server()
