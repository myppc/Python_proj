
from network import *
import numpy as np


net1 = NetWork(NET_INIT)
net2 = NetWork(NET_INIT)
net3,net4 = net1.mix_net_with(net2)

print(net1.feedforward([1,2,3,4,5,6,7]))
print("============")
print(net3.feedforward([1,2,3,4,5,6,7]))