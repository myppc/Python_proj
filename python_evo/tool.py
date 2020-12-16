import random
from OpenGL.GL import *
from OpenGL.GLUT import *
import math
from vector import *
from config import *
from color import *
#在列表中随机挑选指定个数的元素
def pick_item_in_list(srclist,count):
    dict = {}
    while True:
        index = random.randint(0,len(srclist) - 1)
        index_str = str(index)
        if not index_str in dict: 
            item = srclist[index]
            dict[index_str] = item
        if len(dict) == count:
            return list(dict.values())

#向缓存中压入点
def push_point_list(point_list):
    for point in point_list:
        glVertex3f(point.x, point.y, 0)

#向缓存中压入点
def push_point(point):
    glVertex3f(point.x, point.y, 0)


def push_color(color):        
    glColor4f(color.r, color.g, color.b, color.a)

#将格子内坐标转移到窗口坐标
def offset_point_to_cell(point,cell_index):
    cell = index_to_cell(cell_index)
    cell_center = cal_cell_center(cell)
    return cell_center.add(point)

#窗口坐标转格子坐标,窗口坐标在左下角
def px_to_cell(position):
    x = math.floor(position.x/CELL_SIZE)
    y = math.floor((WINDOW_HEIGHT - position.y)/CELL_SIZE)
    return Vector(x,y)

#格子坐标转index
def cell_to_index(cell_vec):
    return cell_vec.y * MAX_X + cell_vec.x


#转换index到格子坐标
def index_to_cell(cell_index):
    x = cell_index%MAX_X
    y = math.floor(cell_index / MAX_X)
    return Vector(x,y,0)

#计算格子中心坐标
def cal_cell_center(cell_vec):
    x = cell_vec.x
    y = cell_vec.y
    x1 = (CELL_SIZE * x + CELL_SIZE/2)/WINDOW_WIDTH * 2 -1 
    y1 = (CELL_SIZE * (MAX_Y - 1 - y) + CELL_SIZE/2)/WINDOW_HEIGHT * 2 -1
    return Vector(x1,y1,0)

#计算格子中心坐标
def cal_cell_center_px(cell_vec):
    x = cell_vec.x
    y = cell_vec.y
    x1 = (CELL_SIZE * x + CELL_SIZE/2)
    y1 = (CELL_SIZE * (MAX_Y - 1 - y) + CELL_SIZE/2)
    return Vector(x1,y1,0)
 
 #获取颜色
def get_color(x, y,width,height):
    size = int(width * height)
    color_list = (GLuint * size)(0)
    #读取点(x,y)的颜色color
    color_list = glReadPixels(x, y, width, height, GL_RGB, GL_UNSIGNED_BYTE, None)
    ret = []
    i = 0
    for y in range(int(height)):
        temp_list = []
        for x in range(int(width)):
            r = color_list[i]
            g = color_list[i + 1]
            b = color_list[i + 2]
            color = Color(r/255., g/255., b/255.,1)
            temp_list.append(color)
            i = i + 3
        temp_list.reverse()
        ret = ret + temp_list 
    ret.reverse()
    return ret


def rgb255_to_hsv(R,G,B):
    r, g, b = R/255.,G/255.,B/255.
    mx = max(r, g, b)
    mn = min(r, g, b)
    m = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        if g >= b:
            h = ((g-b)/m)*60
        else:
            h = ((g-b)/m)*60 + 360
    elif mx == g:
        h = ((b-r)/m)*60 + 120
    elif mx == b:
        h = ((r-g)/m)*60 + 240
    if mx == 0:
        s = 0
    else:
        s = m/mx
    v = mx
    h = h /360 * 255
    s = s * 255.0
    v = v * 255.0
    return [h,s,v]

