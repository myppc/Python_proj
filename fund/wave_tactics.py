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
                    if self.last_dir == 1:
                        self.buy(self.cur_money/2,"买入一半1")
                        
                    elif self.last_dir == -1:
                        self.sell(self.hold_stock/2,"止盈一般")
                self.limit_price = today_avg
            else:
            #当前是平台期
                #平台期均价和当前均价相差3%就视为移出平台期
                if abs(self.limit_price -  today_avg)/self.limit_price * 100 > 3:
                    self.wave_dir = today_dir
                    self.wave.append((self.today,today_avg))
                    if today_dir == 1:
                        self.sell(self.hold_stock,"清仓")
                    elif today_dir == -1:
                        self.buy(self.cur_money/2,"买入一半2")
                        



                

    def fliter_tranding_info(self):
        ret = base_tactics.fliter_tranding_info(self)
        ret["wave"] = self.wave
        return ret

        

