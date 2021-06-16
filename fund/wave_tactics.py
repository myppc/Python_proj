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
        self.limit_price = 0
        

    def today_decision(self):
        today_avg = self.cal_last_average(10)
        last_avg = self.cal_last_average(10,1)
        today_dir = self.wave_dir
        if last_avg > today_avg :
            today_dir = -1
        elif last_avg < today_avg :
            today_dir = 1
        if len(self.wave) == 0:
            self.wave.append((self.today,today_avg))
            self.wave_dir = today_dir
            self.limit_price = today_avg
            return 
        else:
            last_dir = self.wave_dir
            last_wave = self.wave[-1]
            if last_dir != today_dir:
                if abs(self.limit_price -today_avg)/self.limit_price * 100 >2:
                    self.wave_dir = today_dir
                    self.wave.append((self.today,today_avg))
                    self.limit_price = today_avg
                    if last_dir == -1 and today_dir == 1 and self.hold_stock == 0:
                        self.buy(self.cur_money,"满仓")
                        print(self.today,last_dir,today_dir,self.limit_price,today_avg)
                    elif last_dir == 1 and today_dir == -1 and self.hold_stock != 0:
                        self.sell(self.hold_stock,"止盈")

            else:
                self.limit_price = today_avg

                

    def fliter_tranding_info(self):
        ret = base_tactics.fliter_tranding_info(self)
        ret["wave"] = self.wave
        return ret

        

