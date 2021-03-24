import numpy as np
from config import *
import random
import math

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
        z = np.array(z,dtype = np.float64)
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

        if speed_ret < SPEED_DIS:
            speed_ret = -1
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
            
            new_biases1,new_biases2 = self.mute_b(new_biases1,new_biases2)
            new_weights1,new_weights2 = self.mute_w(new_weights1,new_weights2)
            
            child1.append((info[0],new_weights1,new_biases1))
            child2.append((info[0],new_weights2,new_biases2))

        new_b1 = [np.array(item[2]) for item in child1]
        new_b2 = [np.array(item[2]) for item in child2]
        
        new_w1 = [np.array(item[1],dtype=object) for item in child1]
        new_w2 = [np.array(item[1],dtype=object) for item in child2]
        net_child1 = NetWork(NET_INIT,new_b1,new_w1)
        net_child2 = NetWork(NET_INIT,new_b2,new_w2)
        return net_child1,net_child2

    def mute_w(self,new_weights1,new_weights2):
        for index in range(W_MUTE_COUNT): 
            if random.randint(0,100) < MUTE_PER:
                mute_index = random.randint(0,len(new_weights1) -1)
                mute_dir = random.randint(0,100) -50
                if mute_dir == 0:
                    mute_dir = 1
                mute_dir = mute_dir/abs(mute_dir)
                temp = []
                for value in new_weights1[mute_index]:
                    value1 = value + mute_dir * random.uniform(0.1, B_MUTE_DIS) * value
                    temp.append(value1)
                new_weights1[mute_index] = temp
                temp = []
                for value in new_weights2[mute_index]:
                    value2 = value + mute_dir * random.uniform(0.1, B_MUTE_DIS) * value
                    temp.append(value2)
                new_weights2[mute_index] = temp
        return new_weights1,new_weights2
                # value1 = new_biases1[mute_index] + mute_dir * B_MUTE_DIS * new_biases1[mute_index]
                # new_biases1[mute_index] = value
                # value2 = new_biases2[mute_index] + mute_dir * B_MUTE_DIS * new_biases2[mute_index]
                # new_biases2[mute_index] = value

    def mute_b(self,new_biases1,new_biases2):
        for index in range(B_MUTE_COUNT): 
            if random.randint(0,100) < MUTE_PER:
                mute_index = random.randint(0,len(new_biases1) -1)
                mute_dir = random.randint(0,100) -50
                if mute_dir == 0:
                    mute_dir = 1
                mute_dir = mute_dir/abs(mute_dir)
                value_list1 = new_biases1[mute_index]
                temp = []
                for value in value_list1:
                    value = value + mute_dir * random.uniform(0.1, B_MUTE_DIS) * value
                    temp.append(value)
                new_biases1[mute_index] = temp
                
                value_list2 = new_biases2[mute_index]
                temp = []
                for value  in value_list2:
                    value = value + mute_dir * random.uniform(0.1, B_MUTE_DIS) * value
                    temp.append(value)
                new_biases2[mute_index] = temp

        return new_biases1,new_biases2

# if __name__ == '__main__':
#     net = NetWork([7,10,5,2])
#     print(net.feedforward([1,2,2,2,3,4,6,]))
