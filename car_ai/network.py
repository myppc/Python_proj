import numpy as np
from config import *
import random

class NetWork:
    def __init__(self, sizes,b = None,w = None):
        self.num_layers = len(sizes)
        self.sizes = sizes
        if not b:
            self.biases = [np.random.randn(y, 1) for y in sizes[1:]]
        else:
            self.biases = b
        if not w:
            self.weights = [np.random.randn(y, x) for x, y in zip(sizes[:-1], sizes[1:])]
        else:
            self.weights = w

    def sigmoid(self,z):
        ret = 1.0/(1.0+np.exp(-z))
        return ret

    def feedforward(self, a):
        """Return the output of the network if "a" is input."""
        for b, w in zip(self.biases, self.weights):
            a = self.sigmoid(np.dot(w, a)+b)
        dir_flag = a[0]
        speed_flag = a[1]
        dir_ret = np.sum(dir_flag)/np.size(dir_flag)
        speed_ret = np.sum(speed_flag)/np.size(speed_flag)
        if dir_ret < DIS[0]:
            dir_ret = -1
        elif dir_ret < DIS[1]:
            dir_ret = 0
        else:
            dir_ret = 1

        if speed_ret < DIS[0]:
            speed_ret = -1
        elif speed_ret < DIS[1]:
            speed_ret = 0
        else:
            speed_ret = 1

        return dir_ret,speed_ret

    def mix_net_with(self,other):
        mid = NET_INIT[1:len(NET_INIT)]
        layer_indexs = range(1,len(NET_INIT))
        info_list = []
        for index in range(len(layer_indexs)):
            info_list.append((layer_indexs[index]-1,mid[index]))
        
        child1 = []
        child2 = []
        for info in info_list:
            fliter_num = random.randint(1,info[1]-1)
            target_list1 = self.weights[info[0]].tolist()
            target_list2 = other.weights[info[0]].tolist()

            b_list1 = self.biases[info[0]].tolist()
            b_list2 = other.biases[info[0]].tolist()


            new_weights1 = target_list1[:fliter_num]+target_list2[fliter_num:]
            new_weights2 = target_list1[fliter_num:]+target_list2[:fliter_num]

            new_biases1 = b_list1[:fliter_num]+b_list2[fliter_num:]
            new_biases2 = b_list1[fliter_num:]+b_list2[:fliter_num]
            child1.append((info[0],new_weights1,new_biases1))
            child2.append((info[0],new_weights2,new_biases2))

        new_b1 = [np.array(item[2]) for item in child1]
        new_b2 = [np.array(item[2]) for item in child2]
        
        new_w1 = [np.array(item[1]) for item in child1]
        new_w2 = [np.array(item[1]) for item in child2]

        net_child1 = NetWork(NET_INIT,new_b1,new_w1)
        net_child2 = NetWork(NET_INIT,new_b2,new_w2)
        return net_child1,net_child2

# if __name__ == '__main__':
#     net = NetWork([7,10,5,2])
#     print(net.feedforward([1,2,2,2,3,4,6,]))
