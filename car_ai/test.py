
from network import *
import numpy as np


net1 = NetWork(NET_INIT)
net2 = NetWork(NET_INIT)
net3,net4 = net1.mix_net_with(net2)
