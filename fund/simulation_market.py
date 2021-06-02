from loop_tactics import loop_tactics
from tactics import base_tactics
from fund_data_manager import fund_data_manager
import time 

class simulation_market:
    today = ""
    code = ""
    tactics = []
    start_money = 0
    end_day = ""

    def __init__(self):
        pass
    

    def start_round(self):
        self.tactics.append(loop_tactics(self.start_money,self.today,self.code))
        self.tactics.append(base_tactics(self.start_money,self.today,self.code))
        count = 0
        while True:
            today_stamp = time.mktime(time.strptime(self.today,'%Y-%m-%d'))
            endday_stamp = time.mktime(time.strptime(self.end_day,'%Y-%m-%d'))
            if today_stamp >= endday_stamp:
                for item in self.tactics:
                    item.on_end_simulation()
                break
            else:
                self.to_next_around()


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

market = simulation_market()
market.auto_running('320007','2018-06-01','2021-06-01',10000)

