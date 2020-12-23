import numpy as np
from config import *
class NetWork:
    def __init__(self, sizes):
        self.num_layers = len(sizes)
        self.sizes = sizes
        self.biases = [np.random.randn(y, 1) for y in sizes[1:]]
        self.weights = [np.random.randn(y, x) for x, y in zip(sizes[:-1], sizes[1:])]

    def sigmoid(self,z):
        return 1.0/(1.0+np.exp(-z))

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


# if __name__ == '__main__':
#     net = NetWork([7,10,5,2])
#     print(net.feedforward([1,2,2,2,3,4,6,]))
