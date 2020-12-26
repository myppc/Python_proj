import numpy as np
from socket_link  import *
from network import *
from config import *
import copy

class Main:
    net_list = {}
    def __init__(self):
        self.net_list = {}
        self.socket = socket_server()
        self.socket.set_receive_data_call_back(self.data_filter)
        self.socket.start_listener()

        

    def data_filter(self,data):
        msg = str(data)
        ret = self.cut_str(msg,[])
        for item in ret:
            split_list = item.split(',')
            self.cmd(split_list)
    
    def cmd(self,split_list):
        cmd = split_list[0]
        if cmd == CMD["NET_MOVE"]: #[cmd,index,d1...d7]
            self.net_run(split_list)
        elif cmd == CMD["CREATE"]:  #[cmd,index]
            self.create_net(split_list[1])
        elif cmd == CMD["CLEAR"]:#[cmd]
            self.clear()
        elif cmd == CMD["CHOOSE_NEXT"]:#[cmd,index1...indexN]
            self.create_next_net(split_list)

    def create_next_net(self,split_list):
        print("create_next ",split_list)
        copy_list = []
        
        for index in range(1,len(split_list)):
            id = split_list[index]
            item = copy.deepcopy(self.net_list[id])
            copy_list.append(item)
        self.clear()
        parent_index_list = np.random.randint(len(copy_list),size = (int(CAR_NUM/2),2))
        count = 0
        for item in parent_index_list:
            child1,child2 = copy_list[item[0]].mix_net_with(copy_list[item[1]])
            self.net_list[str(count)] = child1
            count = count + 1
            self.net_list[str(count)] = child2
            count = count + 1
        msg = "s"+ CMD["NEXT_READY"]+ "e"
        self.socket.sendMsg(msg)
        
    def clear(self):
        self.net_list = {}

    def net_run(self,data):
        index = data[1]
        if not index in self.net_list:
            return
        net = self.net_list[index]
        if net == None:
            return
        list = []
        for index in range(2,len(data)):
            list.append(float(data[index]))
        
        dir_ret,speed_ret = net.feedforward(list)
        msg = "s"+ CMD["CONTROL"]+"," + str(data[1])+"," + str(dir_ret)+","+str(speed_ret) + "e"
        self.socket.sendMsg(msg)

    def cut_str(self,msg,ret):
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