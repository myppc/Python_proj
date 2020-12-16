#比较两张图片的相似度
from PIL import Image
from functools import reduce
import time
import tool 
import numpy as np
from config import *
# 计算Hash
# def phash(img):
#     img = img.resize((50, 50), Image.ANTIALIAS).convert('L')
#     avg = reduce(lambda x, y: x + y, img.getdata()) / (50 * 50.)
#     return reduce(
#         lambda x, y: x | (y[1] << y[0]),
#         enumerate(map(lambda i: 0 if i < avg else 1, img.getdata())),
#         0
#     )

# 计算汉明距离
def hamming_distance(a, b):
    return bin(a ^ b).count('1')

# 计算图片相似度
# def is_imgs_similar(img1, img2):
#     return hamming_distance(phash(img1), phash(img2))

# 计算图片相似度
def is_imgs_similar(img1, img2):
    list1 = get_hsv_list(img1)
    list2 = get_hsv_list(img2)
    l1 = np.asarray(list1)
    l2 = np.asarray(list2)
    dis = np.subtract(l1,l2)
    dis = np.maximum(dis, -dis)
    avg = dis.sum()/np.size(dis)
    list_dis = dis.tolist()
    ret = reduce(
        lambda x, y: x | (y[1] << y[0]),
        enumerate(map(lambda i: 0 if i < avg else 1,list_dis)),
        0
    )
    return bin(ret).count('1')

def get_hsv_list(src_img):
    img = src_img.resize((COMPARE_IMG_SIZE,COMPARE_IMG_SIZE), Image.ANTIALIAS)
    hsv_list = []
    for color in img.getdata():
        hsv_list = hsv_list + tool.rgb255_to_hsv(color[0],color[1],color[2])
    return hsv_list

# if __name__ == '__main__':
#     img1_path = 'demo.png'
#     img2_path = "demo2.png"

#     img1 = Image.open(img1_path)
#     img2 = Image.open(img2_path)
    
#     start_time =time.time()
#     a = is_imgs_similar(img1, img2)
#     end_time = time.time()
#     print(a,end_time-start_time)