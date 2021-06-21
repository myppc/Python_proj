import numpy as np
from fund_data_manager import fund_data_manager
import time
import math
from tactics import base_tactics

class wave_tactics(base_tactics):
    tag = "WAVE"
    start_money = 0
    cur_money = 0
    hold_stock = 0
    hold_price = 0 #持仓价
    start_day = ""
    today = ""
    record_list = []
    today_trading_money = 0
    today_sell_vol = 0
    code = ''
    temp_data = {}
    buy_list = []
    risk_per = 0.15
    wave = []
    wave_dir = 0

    def __init__(self,start_money,start_day,code):
        base_tactics.__init__(self,start_money,start_day,code)
        self.wave = []
        self.wave_dir = 0
        self.last_dir = 0
        self.limit_price = 0
        

    def today_decision(self):
        today_data = fund_data_manager.get_ins().get_day_data(self.code,self.today)
        if today_data == "sub":
            return
        cur_price = today_data[1] #当前价格
        hold_price = self.cal_hold_avg_price()#持有成本价格
        last_price = self.find_last_limit_price(20)
        avg10 = self.cal_last_average(10)
        min_20 = last_price[0]
        max_20 = last_price[1]
        

        if self.hold_stock ==0 : 
            if cur_price > max_20:
                self.buy(self.last_money  * 0.25,"突破二十日最大值")
                return
        else:
            last_buy_day = self.trading_list[-1][2]
            cur_time_stamp = time.mktime(time.strptime(self.today,'%Y-%m-%d'))
            last_time_stamp = time.mktime(time.strptime(last_buy_day,'%Y-%m-%d'))
            if (avg10 - cur_price)/avg10 > 0.05 and (cur_time_stamp - last_time_stamp) /(24*3600) > 5:
                self.sell_per -= 10
                self.sell_per = max(self.sell_per,100)
                self.buy(self.cur_money  * 0.1,"补仓")
                return;
            if (cur_price - hold_price)/hold_price * 100 > 20 :
                self.sell_per = 100
                self.sell(self.hold_stock ,"止盈")
                return;

        today_avg = self.cal_last_average(5)
        last_avg = self.cal_last_average(5,1)
        today_dir = self.wave_dir
        if last_avg > today_avg :
            today_dir = -1
        elif last_avg < today_avg :
            today_dir = 1
        if len(self.wave) == 0:
            self.wave.append((self.today,today_avg))
            self.wave_dir = today_dir
            self.last_dir = today_dir
            self.limit_price = today_avg
            return 
        else:
            cur_dir = self.wave_dir
            #当前不是平台期
            if cur_dir != 0:
                #出现方向变化，转入平台期
                if cur_dir != today_dir:
                    self.last_dir = self.wave_dir
                    self.wave_dir = 0
                    self.wave.append((self.today,today_avg))
                self.limit_price = today_avg
            else:
            #当前是平台期
                #平台期均价和当前均价相差3%就视为移出平台期
                if abs(self.limit_price -  today_avg)/self.limit_price * 100 > 3:
                    self.wave_dir = today_dir
                    self.wave.append((self.today,today_avg))
                    if today_dir == 1:
                        self.sell(self.hold_stock/2,"止盈1/2")
                    if today_dir == -1:
                        if hold_price > cur_price:
                            self.buy(self.cur_money/4,"继续加仓")
                        else:
                            self.sell(self.hold_stock,"清仓")

                        



                

    def fliter_tranding_info(self):
        ret = base_tactics.fliter_tranding_info(self)
        ret["wave"] = self.wave
        return ret

        

