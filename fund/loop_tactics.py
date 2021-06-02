
from fund_data_manager import fund_data_manager
import time
import math
from tactics import base_tactics

class loop_tactics(base_tactics):
    tag = "LOOP"
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

    def today_decision(self):
        today_data = fund_data_manager.get_ins().get_day_data(self.code,self.today)
        cur_price = today_data[1]
        hold_price = self.cal_hold_avg_price()
        if self.hold_stock != 0:
            
            if cur_price / hold_price > 1 + self.risk_per*2:
                self.sell(self.hold_stock)
                return

        if len(self.buy_list) == 0:
            self.buy(self.start_money/100)
        else:
            if self.cur_money > 0:
                last_buy_day = self.buy_list[-1][2]
                cur_time_stamp = time.mktime(time.strptime(self.today,'%Y-%m-%d'))
                last_time_stamp = time.mktime(time.strptime(last_buy_day,'%Y-%m-%d'))
                if (cur_time_stamp - last_time_stamp) /(24*3600) > 5:
                    self.buy(self.start_money/100)
            elif cur_price / hold_price > 1 + self.risk_per:
                self.sell(math.floor(self.hold_stock/2))

        

