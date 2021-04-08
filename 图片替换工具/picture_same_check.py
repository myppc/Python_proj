#比较两张图片的相似度
from PIL import Image
from functools import reduce
import time


def phash(img):
    img = img.resize((32, 32), Image.ANTIALIAS).convert('L')
    avg = reduce(lambda x, y: x + y, img.getdata()) / (32. * 32.)
    return reduce(
        lambda x, y: x | (y[1] << y[0]),
        enumerate(map(lambda i: 0 if i < avg else 1, img.getdata())),
        0
    )
# 计算汉明距离
def hamming_distance(a, b):
    return bin(a ^ b).count('1')
# 计算图片相似度
def is_imgs_similar(img1, img2):
    return True if hamming_distance(phash(img1), phash(img2)) <= 5 else False

def check(path1,path2):
    img1 = Image.open(path1)
    img2 = Image.open(path2)
    return is_imgs_similar(img1, img2)