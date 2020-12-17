from dna import *
import random
import tool
from config import *
from img_dis import *
from PIL import Image
class Person():
    dna_list = []
    index = 0

    def __init__(self):
        self.dna_list = []
        self.index = 0


    def create_all_dna(self):
        self.dna_list = []
        for i in range(DNA_COUNT):
            dna = Dna()
            dna.random_dna_data()
            self.dna_list.append(dna)

    #dna 变异
    def mutate_dna(self,count):
        if count > DNA_COUNT:
            count = DNA_COUNT
        for i in range(count):
            if random.randint(0,100) < MUTE_PER:
                index = random.randint(0,len(self.dna_list)-1)
                self.mutate_dna_by_index(index)

    #变异指定dna
    def mutate_dna_by_index(self,index):
        old_dna = self.dna_list[index]
        new_dna = Dna()
        new_dna.random_dna_data()
        self.dna_list[index] = new_dna

            
    #设置index        
    def set_index(self,index):
        self.index = index

    #设置dna_list       
    def set_dna_list(self,dna_list):
        self.dna_list = dna_list

    #繁殖个体
    def create_son(self,parent,mutate_dna_count):
        self_list = tool.pick_item_in_list(self.dna_list,len(self.dna_list)/2)
        parent_list = tool.pick_item_in_list(parent.dna_list,len(parent.dna_list)/2)
        pool = {}
        for dna in self.dna_list:
            if not str(dna.id) in pool:
                pool[str(dna.id)] = dna
        
        for dna in parent.dna_list:
            if not str(dna.id) in pool:
                pool[str(dna.id)] = dna
        
        dna_list = tool.pick_item_in_list(list(pool.values()),DNA_COUNT)
        son = Person()
        son_dna_list = []
        for i in dna_list:
            son_dna_list.append(i.copy())
        son.set_dna_list(son_dna_list)
        son.mutate_dna(mutate_dna_count)
        return son

    
    def draw_person(self):
        for dna in self.dna_list:
            dna.draw_dna(self.index)    

    def get_cur_color_list(self):
        cell = tool.index_to_cell(self.index)
        person_px_center = tool.cal_cell_center_px(cell)
        x = person_px_center.x - CELL_SIZE/2
        y = person_px_center.y - CELL_SIZE/2
        color_list = tool.get_color(x,y,CELL_SIZE,CELL_SIZE)
        
        return color_list
    
    def get_cur_image(self):
        image_width, image_height = 50, 50
        # 填充占位数据
        image_bytes = bytearray([0x70, 0x70, 0x70]) * image_width * image_height
        color_list = self.get_cur_color_list()
        i = 0
        # 设置颜色渐变
        for color in color_list:
            image_bytes[i] = int(color.r *255)  # R
            image_bytes[i + 1] = int(color.g *255)  # G
            image_bytes[i + 2] = int(color.b *255)  # B
            i = i + 3
        # 注意这里与 frombytes 的不同，无后面四个参数会出现警告信息
        image = Image.frombuffer('RGB', (image_width, image_height), bytes(image_bytes), 'raw', 'RGB', 0, 1)
        return image

    def cal_score(self,dest_img):
        self_img = self.get_cur_image()
        dis = is_imgs_similar(dest_img,self_img)
        return dis 

    def copy(self):
        copy_person = Person()
        copy_dna_list = []
        for i in self.dna_list:
            copy_dna_list.append(i.copy())
        copy_person.set_dna_list(copy_dna_list)
        copy_person.set_index(self.index)
        return copy_person




