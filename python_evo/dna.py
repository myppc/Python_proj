from vector import *
import random
from color import *
import tool 
from config import *
class Dna:
    vec_list = []
    color = []
    id = 0

    def __init__(self):
        self.vec_list = []
        self.color = []
        global DNA_ID
        DNA_ID = DNA_ID + 1
        self.id = DNA_ID

    def set_id(self,id):
        self.id = id

    #随机点位子
    def random_vec_list(self):
        while True:
            self.vec_list = []
            for i in range(3):
                vec = Vector.random_vec(-1000,1000)
                vec.x = vec.x/1000
                vec.y = vec.y/1000
                self.vec_list.append(vec)
            if self.isvalid():
                size = self.calculate_area()
                if size < 0.3 and size > 0.1:
                    break

    def isvalid(self):
        x1, y1 = self.vec_list[0].x,self.vec_list[0].y
        x2, y2 = self.vec_list[1].x,self.vec_list[1].y
        x3, y3 = self.vec_list[2].x,self.vec_list[2].y

        # 计算三条边长
        side1 = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        side2 = math.sqrt((x1 - x3) ** 2 + (y1 - y3) ** 2)
        side3 = math.sqrt((x2 - x3) ** 2 + (y2 - y3) ** 2)
        side = [side1, side2, side3]
        side.sort()
        if side[0] + side[1] > side[2] or side[2] - side[1] < side[0]:
            return True
        else:
            return False


    def calculate_area(self):
        x1, y1 = self.vec_list[0].x,self.vec_list[0].y
        x2, y2 = self.vec_list[1].x,self.vec_list[1].y
        x3, y3 = self.vec_list[2].x,self.vec_list[2].y

        # 计算三条边长
        side1 = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        side2 = math.sqrt((x1 - x3) ** 2 + (y1 - y3) ** 2)
        side3 = math.sqrt((x2 - x3) ** 2 + (y2 - y3) ** 2)

        # 计算半周长
        s = (side1 + side2 + side3) / 2
        # 计算面积
        area = (s * (s - side1) * (s - side2) * (s - side3)) ** 0.5
        return area


            
    #随机颜色
    def random_color(self):
        self.color = Color()
        self.color.random_color(180)


    #随机dna信息
    def random_dna_data(self):
        self.random_vec_list()
        self.random_color()

    def set_vec_list(self,vec_list):
        self.vec_list = vec_list

    def set_color(self,color):
        self.color = color

    #绘制dna
    def draw_dna(self,person_index):
        tool.push_color(self.color)
        for point in self.vec_list:
            tool.push_color(self.color)
            x = point.x * CELL_SIZE /WINDOW_WIDTH
            y = point.y * CELL_SIZE /WINDOW_WIDTH
            vec = tool.offset_point_to_cell(Vector(x,y),person_index)
            tool.push_point(vec)

    def copy(self):
        dna = Dna()
        copy_list = []
        for vec in self.vec_list:
            copy_list.append(vec.copy())
        dna.set_vec_list(copy_list)
        dna.set_color(self.color.copy())
        dna.set_id(self.id)
        return dna

    def tostring(self):
        info = ""
        info = info + str(self.id) + " "
        for vec in self.vec_list:
            info = info + vec.tostring() +" | "
        info = info + self.color.tostring()
        return info

        