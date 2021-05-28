from fund_data_manager import fund_data_manager
import time 

class simulation_market:
    today = ""
    code = ""

    def __init__(self):
        pass
    

    def get_today_data(self):
        today_data = fund_data_manager.get_ins().get_day_data(self.code,self.today)

    def start_round(self):
        pass

    def to_next_around(self):
        self.cal_next_day()
    
    def cal_next_day(self):
        target_day = time.strptime(self.today,'%Y-%m-%d')
        target_stamp = time.mktime(target_day)
        target_stamp+= 3600 *24
        next_day = time.localtime(target_stamp)
        self.today = "{0}-{1}-{2}".format(str(next_day[0]).zfill(2),str(next_day[1]).zfill(2),str(next_day[2]).zfill(2))
        print(self.today)


    def auto_running(self,code,start_day,start_money):
        self.today = start_day
        self.code = code
        self.start_round()


