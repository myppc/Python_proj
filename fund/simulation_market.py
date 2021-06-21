from loop_tactics import loop_tactics
from wave_tactics import wave_tactics
from every_day_tactics import every_day_tactics
from tactics import base_tactics
from fund_data_manager import fund_data_manager
import time 
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator
import fund_data_puller
from db.db_loader_helper import db_loader

class simulation_market:
    today = ""
    code = None
    tactics = []
    start_money = 0
    end_day = ""

    def __init__(self):
        self.today = ""
        self.code = None
        self.tactics = []
        self.start_money = 0
        self.end_day = ""
        pass
    

    def start_round(self):
        self.tactics.append(wave_tactics(self.start_money,self.today,self.code))
        count = 0
        while True:
            today_stamp = time.mktime(time.strptime(self.today,'%Y-%m-%d'))
            endday_stamp = time.mktime(time.strptime(self.end_day,'%Y-%m-%d'))
            if today_stamp >= endday_stamp:
                self.simulation()
                if input("显示折线图？(Y/N) ") == "y":
                    ret = self.filter_tactic_record()
                    self.draw_plt(ret)
                break
            else:
                self.to_next_around()

    def filter_tactic_record(self):
        tactic = self.tactics[0]
        ret = tactic.fliter_tranding_info()
        return ret

    def simulation(self):
        tactic = self.tactics[0]
        tactic.on_end_simulation()

    def close_plt(self):
        plt.close()

    def draw_plt(self,data):
        price = data["price"]
        record = data["record"]
        date = data["date"]
        avg = data["avg"]
        wave = None

        plt.plot(date,price)#s-:方形
        plt.plot(date,avg,color='green')#s-:方形
        if "wave" in data:
            wave = data["wave"]
            wave_price = []
            wave_date = []
            for item in wave:
                wave_date.append(item[0])
                wave_price.append(item[1])
                #plt.scatter(item[0],item[1],c = item[2])
            plt.plot(wave_date,wave_price,color='red',linestyle ="--")#s-:方形        
        
        x_major_locator = MultipleLocator(10)
        ax = plt.gca()
        ax.xaxis.set_major_locator(x_major_locator)
        plt.xticks(rotation=45,size =7)
        for point_info in record:
            x = point_info[0]
            y = point_info[1]
            c = "blue"
            if point_info[2] == "BUY":
                c = "red"
            plt.scatter(x,y,c = c)
        plt.show()

    def to_next_around(self):
        endday_stamp = time.mktime(time.strptime(self.end_day,'%Y-%m-%d'))
        while True:
            if self.cal_next_day():
                break
            today_stamp = time.mktime(time.strptime(self.today,'%Y-%m-%d'))
            if today_stamp >= endday_stamp:
                break
        for item in self.tactics:
            item.on_end_today(self.today)
    
    def cal_next_day(self):

        target_day = time.strptime(self.today,'%Y-%m-%d')
        target_stamp = time.mktime(target_day)
        target_stamp+= 3600 *24
        next_day = time.localtime(target_stamp)
        self.today = "{0}-{1}-{2}".format(str(next_day[0]).zfill(2),str(next_day[1]).zfill(2),str(next_day[2]).zfill(2))
        if fund_data_manager.get_ins().get_day_data(self.code,self.today) == "sub":
            return False
        else:
            return True


    def auto_running(self,code,start_day,end_day,start_money):
        self.today = start_day
        self.code = code
        self.start_money = start_money
        self.end_day = end_day
        self.start_round()


    def handel_running(self):
        self.code = int(input("input code "))
        self.today = input("start_date ") 
        self.start_money = int(input("start_money "))
        self.end_day = input("end_date ") 
        self.tactics.append(every_day_tactics(self.start_money,self.today,self.code))
        count = 0
        while True:
            today_stamp = time.mktime(time.strptime(self.today,'%Y-%m-%d'))
            endday_stamp = time.mktime(time.strptime(self.end_day,'%Y-%m-%d'))
            if today_stamp >= endday_stamp:
                self.simulation()
                if input("显示折线图？(Y/N) ") == "y":
                    ret = self.filter_tactic_record()
                    self.draw_plt(ret)
                break
            else:
                self.to_next_around()

    def handel_today(self):
        if self.code == None :
            self.code = input("input code = ")
        else:
            print("====================> handel ",self.code)
        is_exist = fund_data_manager.get_ins().check_fund_data_exist(self.code)
        if not is_exist:
            print("缺少基础数据库，需要先checkout当前基金数据")
            fund_data_puller.main()
        tactics = None

        if fund_data_manager.get_ins().check_fund_data_exist("running_data_"+self.code):
            print("加载交易进程")
            tactics = every_day_tactics(0,"",self.code)
            tactics.load_today()
        else:
            print("不存在该进程")
            if input("初始化交易进程？(Y/N) ") == "y":
                start_date = input("start date (year-mon-day) " )
                if start_date == "":
                    today_struct = time.localtime()
                    start_date = "{0}-{1}-{2}".format(str(today_struct[0]).zfill(2),str(today_struct[1]).zfill(2),str(today_struct[2]).zfill(2))
                start_money = input("start money ")
                tactics = every_day_tactics(int(start_money),start_date,self.code)
                db_loader.get_ins().load_db("running_data_"+self.code)
            else:
                return
        self.tactics.append(tactics)
        if fund_data_manager.get_ins().check_today_need_pull(self.code):
            tactics.update_db_data()
        today_struct = time.localtime()
        today = "{0}-{1}-{2}".format(str(today_struct[0]).zfill(2),str(today_struct[1]).zfill(2),str(today_struct[2]).zfill(2))
        print("今日交易日期",today,"操作代码",self.code)
        is_go = True
        self.today = today
        tactics.on_end_today(self.today)
        self.simulation()
        tactics.save_today()
        if input("显示折线图？(Y/N) ") == "y":
            ret = self.filter_tactic_record()
            self.draw_plt(ret)





