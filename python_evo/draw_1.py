# -*- coding: utf-8 -*-

# -------------------------------------------
# quidam_01.py 三维空间的世界坐标系和三角形
# -------------------------------------------
import matplotlib.pyplot as plt
from color import *
import numpy as np
import time
from OpenGL.GL import *
from OpenGL.GLUT import *
import math
from team import *
from config import *
import tool 
from PIL import Image
class Evo:
    team = []
    def init_evo(self):
        self.team = Team()
        self.team.init_team(MAX_X * MAX_Y)



def draw():
    glClearColor(1, 1, 1, 1.0) # 设置画布背景色。注意：这里必须是4个参数
    glClear(GL_COLOR_BUFFER_BIT);
    # ---------------------------------------------------------------
    glBegin(GL_TRIANGLES)                # 开始绘制三角形（z轴负半区）
    get_draw_info()
    glEnd()                              # 结束绘制三角形
    # ---------------------------------------------------------------
    glFlush()                            # 清空缓冲区，将指令送往硬件立即执行

def on_time_call(value):
    evo.team.create_next_list()
    glutPostRedisplay()
    glutTimerFunc(FRAME_TIME,on_time_call,1)


def on_mouse_touch(button, state, x, y):
    if state == 0:
        global STATE
        STATE = "TAG"
        cell = tool.px_to_cell(Vector(x,WINDOW_HEIGHT - y))
        index = tool.cell_to_index(cell)
        copy_person = evo.team.person_list[index].copy()
        color_list = evo.team.person_list[index].get_cur_color_list()
        print("-------- index ",index,evo.team.person_list[index].index)
        global temp_person
        temp_person = copy_person
        count = 0
        image_width, image_height = 50, 50
        # 填充占位数据
        image_bytes = bytearray([0x70, 0x70, 0x70]) * image_width * image_height
        i = 0
        # 设置颜色渐变
        for color in color_list:
            image_bytes[i] = int(color.r *255)  # R
            image_bytes[i + 1] = int(color.g *255)  # G
            image_bytes[i + 2] = int(color.b *255)  # B
            i = i + 3
        # 注意这里与 frombytes 的不同，无后面四个参数会出现警告信息
        image = Image.frombuffer('RGB', (image_width, image_height), bytes(image_bytes), 'raw', 'RGB', 0, 1)
        image.show()


def get_draw_info():
    global STATE
    global temp_person
    if STATE == "NORMAL":
        evo.team.draw_team()
    elif STATE == "TAG":
        if temp_person != None:
            temp_person.draw_person()
    elif STATE == "GET_COLOR":
        glColor4f(1,0,0,1)
        glVertex3f(-1, 1, 0)
        glVertex3f(0, 1, 0)
        glVertex3f(0, 0, 0)

        glColor4f(0,1,0,1)
        glVertex3f(-1, 1, 0)
        glVertex3f(-1, 0, 0)
        glVertex3f(0, 0, 0)


def read_demo():
    img_path = "demo.png"
    img = Image.open(img_path)
    return img

if __name__ == "__main__":
    global temp_person
    temp_person = None
    dest_img = read_demo()
    evo = Evo()
    evo.init_evo()
    evo.team.set_dest_data(dest_img)
    glutInit()                           # 1. 初始化glut库
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutCreateWindow('OpenGL') # 2. 创建glut窗口
    glEnable(GL_BLEND); # 打开混合
    glutInitDisplayMode(GLUT_RGB)
    glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA); # 基于源象素alpha通道值的半透明混合函数
    glutDisplayFunc(draw)                # 3. 注册回调函数draw()
    glutTimerFunc(FRAME_TIME,on_time_call,1)
    glutMouseFunc(on_mouse_touch)
    glutMainLoop()


