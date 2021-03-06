from person import *
import tool
from config import *
class Team:
    person_list = []
    dest_img = []
    dest_per = INIT_DEST_PER
    max_per = 0
    count = 0
    last_max_count = 0
    #初始化族群
    def init_team(self,count):
        self.dest_per = 0
        for i in range(count):
            person = Person()
            person.set_index(i)
            person.create_all_dna()
            self.person_list.append(person)
    
    #设置目标数据
    def set_dest_data(self,dest_img):
        self.dest_img = dest_img

    #设置族群
    def set_person_list(self,list):
        self.person_list = list

    #排序
    def sort_list(self):
        sort_list = []
        for person in self.person_list:
            score = person.cal_score(self.dest_img)
            if len(sort_list) == 0:
                sort_list.append((person,score))
            else:
                is_insert = False
                for index in range(len(sort_list)):
                    if score > sort_list[index][1]:
                        sort_list.insert(index, (person,score))
                        is_insert = True
                        break
                if not is_insert:
                    sort_list.append((person,score))
                    
        ret = []
        for index in range(len(sort_list)):
            ret.append(sort_list[index][0])
        self.person_list = ret
        if sort_list[0][1] > self.max_per:
            self.max_per = sort_list[0][1]
            self.last_max_count = self.count
        print(str(self.count) + "===============> max " ,sort_list[0][1],self.last_max_count )

    #繁殖下一代
    def create_next_list(self):
        self.count = self.count + 1
        mute_num = MUTE_NUM
        if (self.count - self.last_max_count)%100 == 0:
            mute_num = MUTE_NUM * 2
        self.sort_list()
        max_count = len(self.person_list)
        parents_list = self.person_list[0:FILTER_COUNT]
        best = self.person_list[0]
        ret = []
        for i in range(max_count):
            parents = tool.pick_item_in_list(parents_list,2)
            son = parents[0].create_son(parents[1],mute_num)
            son.set_index(i)
            ret.append(son)
        self.person_list = ret
        self.person_list[best.index] = best

    def draw_team(self):
        for person in self.person_list:
            person.draw_person()
        
            
