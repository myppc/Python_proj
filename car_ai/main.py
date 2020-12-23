import numpy as np
from socket_link  import *
from network import *
from config import *

class Main:
    def __init__(self):
        self.socket = socket_server()
        self.socket.set_receive_data_call_back(self.data_filter)
        self.socket.start_listener()
        self.net_list = {}

    def data_filter(self,data):
        msg = str(data)
        ret = self.cut_str(msg)
        ret = ret[-1]
        if ret == None:
            return
        split_list = ret.split(',')
        self.cmd(split_list)
    
    def cmd(self,split_list):
        cmd = split_list[0]
        if cmd == CMD["NET_MOVE"]: #[cmd,index,d1...d7]
            self.net_run(split_list)
        elif cmd == CMD["CREATE"]:  #[cmd,index]
            self.create_net(split_list[1])
        

    def net_run(self,data):
        index = data[1]
        net = self.net_list[index]
        if net == None:
            return
        list = []
        for index in range(2,len(data)):
            list.append(float(data[index]))
        
        dir_ret,speed_ret = net.feedforward(list)
        msg = "s" + index+"," + str(dir_ret)+","+str(speed_ret) + "e"
        self.socket.sendMsg(msg)

    def cut_str(self,msg,ret = []):
        s_pos = msg.find('s')
        if s_pos == -1:
            return ret;
        else:
            e_pos = msg.find('e')
            ret.append(msg[s_pos+1:e_pos])
            msg = msg[e_pos+1:]           
            ret = self.cut_str(msg,ret)
        return ret

    def create_net(self,index):
        self.net_list[index] = NetWork(NET_INIT)

main = Main()