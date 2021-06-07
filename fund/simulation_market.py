from loop_tactics import loop_tactics
from every_day_tactics import every_day_tactics
from tactics import base_tactics
from fund_data_manager import fund_data_manager
import time 
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator

class simulation_market:
    today = ""
    code = ""
    tactics = []
    start_money = 0
    end_day = ""

    def __init__(self):
        pass
    

    def start_round(self):
        self.tactics.append(base_tactics(self.start_money,self.today,self.code))
        count = 0
        while True:
            today_stamp = time.mktime(time.strptime(self.today,'%Y-%m-%d'))
            endday_stamp = time.mktime(time.strptime(self.end_day,'%Y-%m-%d'))
            if today_stamp >= endday_stamp:
                ret = self.simulation()
                if input("显示折线图？(Y/N) ") == "y":
                    self.draw_plt(ret)
                break
            else:
                self.to_next_around()

    def simulation(self):
        price_list = []
        price_date = []
        tactic = self.tactics[0]
        tactic.on_end_simulation()
        tactic_record = tactic.fliter_tranding_info()
        for price_item in tactic.price_list:
            price_list.append(price_item[0])
            price_date.append(price_item[1])

        ret = {"price":price_list,"record":tactic_record,"date":price_date}
        return ret

    def draw_plt(self,data):
        price = data["price"]
        record = data["record"]
        date = data["date"]
        plt.plot(date,price)#s-:方形
        x_major_locator = MultipleLocator(10)
        ax = plt.gca()
        ax.xaxis.set_major_locator(x_major_locator)
        plt.xticks(rotation=45,size =7)
        for point_info in record:
            x = point_info[0]
            y = price[x - 1]
            c = "blue"
            if point_info[1] == "BUY":
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


    def handel_simulation(self):
        self.code = input("input code ")
        self.today = input("start_date ") 
        self.start_money = input("start_money ") 
        self.end_day = input("end_date ") 
        self.tactics.append(every_day_tactics(self.start_money,self.today,self.code))
        count = 0
        while True:
            today_stamp = time.mktime(time.strptime(self.today,'%Y-%m-%d'))
            endday_stamp = time.mktime(time.strptime(self.end_day,'%Y-%m-%d'))
            if today_stamp >= endday_stamp:
                ret = self.simulation()
                if input("显示折线图？(Y/N) ") == "y":
                    self.draw_plt(ret)
                break
            else:
                self.to_next_around()
                if input("next day ? ") == "n":
                    ret = self.simulation()
                    if input("显示折线图？(Y/N) ") == "y":
                        self.draw_plt(ret)
                    break




market = simulation_market()

#market.auto_running('320007','2018-06-05','2021-06-01',10000)
#market.auto_running('001938','2020-07-28','2021-06-01',10000)
#market.auto_running('519674','2020-06-01','2021-06-01',10000)
#market.auto_running('164403','2020-07-27','2021-06-03',10000)
#market.auto_running('004243','2020-06-01','2021-06-02',10000)
#market.auto_running('009777','2020-08-20','2021-06-03',10000)


