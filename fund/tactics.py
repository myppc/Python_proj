
from fund_data_manager import fund_data_manager
import time
import math
import json


class base_tactics:
    tag = "BASE"
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
    price_list = []

    def __init__(self,start_money,start_day,code):
        self.cur_money = start_money
        self.last_all_money = start_money
        self.start_money = start_money
        self.start_day = start_day
        self.today = start_day
        self.code = code
        self.temp_data = {}
        self.buy_list = [] #零时记录购买价格
        self.sell_list = []
        self.price_list = [] #每日交易价格

    def save_result(self):
        f = open(".\\result\\simulation_"+self.tag+"_"+str(self.code)+".txt","w+",encoding = "UTF-8")
        msg = ""
        for info in self.record_list:
            msg = msg + json.dumps(info) +"\n"
        f.write(msg)
        f.close()

    def fliter_tranding_info(self):
        ret = []
        for item in self.record_list:
            ret.append((item["index"],item["act"]))
        return ret

    def on_end_simulation(self):
        hold_price = self.cal_hold_avg_price()
        today_data = fund_data_manager.get_ins().get_day_data(self.code,self.today)
        cur_price = today_data[1]
        all_money = self.hold_stock * cur_price + self.cur_money
        print(self.tag,self.today,self.code,"cur_money",self.cur_money,"cur_pric",cur_price,"hold_stock",self.hold_stock,"hold_price",hold_price,"all_money",all_money)
        self.save_result()

    def buy(self,money):
        if len(self.buy_list) != 0:
            info = self.buy_list[-1]
            date = info[2]
            last_price = info[3]
            avg20 = self.cal_last_average(20)
            cur_time_stamp = time.mktime(time.strptime(self.today,'%Y-%m-%d'))
            last_time_stamp = time.mktime(time.strptime(date,'%Y-%m-%d'))
            if abs(last_price - avg20)/avg20 < 0.03  or (cur_time_stamp - last_time_stamp)/(24 * 3600) < 5:
                return
        money = min(self.cur_money , money)
        money = math.floor(money)
        if money < 10:
            return 
        self.cur_money = self.cur_money - money
        self.today_trading_money = money

    def sell(self,stock_vol):
        if len(self.sell_list) != 0:
            info = self.sell_list[-1]
            date = info[2]
            last_price = info[3]
            avg20 = self.cal_last_average(20)
            cur_time_stamp = time.mktime(time.strptime(self.today,'%Y-%m-%d'))
            last_time_stamp = time.mktime(time.strptime(date,'%Y-%m-%d'))
            if abs(last_price - avg20)/avg20 < self.risk_per/2  or (cur_time_stamp - last_time_stamp)/(24 * 3600) < 5:
                return
        stock_vol = math.floor(stock_vol)
        stock_vol = min(self.hold_stock , stock_vol)
        self.hold_stock = self.hold_stock - stock_vol
        self.today_sell_vol = stock_vol
        if self.hold_stock < 1:
            self.today_sell_vol += self.hold_stock
            self.hold_stock = 0

    def on_end_today(self,next_day):
        today_data = fund_data_manager.get_ins().get_day_data(self.code,self.today)
        if today_data != "sub":
            self.settlement(today_data)
            self.today_decision()
            self.today = next_day

    def settlement(self,today_data):
        price = today_data[1]
        self.price_list.append(price)
        if self.today_sell_vol != 0:
            money = price * self.today_sell_vol
            self.cur_money += money
            self.record_action("SELL",self.today_sell_vol,price)
            self.sell_list.append([self.today_sell_vol,money,self.today,price])
            self.today_sell_vol = 0
            if self.hold_stock == 0:
                self.last_all_money = self.cur_money
                self.clear_buy_list()        
        if self.today_trading_money != 0:
            vol = self.today_trading_money/price
            #计算份额
            self.hold_stock += vol
            self.record_action("BUY",vol,price)
            self.buy_list.append([vol,self.today_trading_money,self.today,price])
            self.today_trading_money = 0



    def record_action(self,act,trading_vol,trading_price):
        all_money = self.hold_stock * trading_price
        act_record = {
            'date':self.today,
            'act':act,
            'trading_vol':trading_vol,
            'hold_stock':self.hold_stock,
            'trading_price':trading_price,
            'cur_money':self.cur_money,
            'all_money':all_money + self.cur_money,
            'index':len(self.price_list)}
        self.record_list.append(act_record)

    def cal_last_average(self,max_day):
        today = time.strptime(self.today,'%Y-%m-%d')
        cur_time_stamp = time.mktime(today)
        avg_price = 0
        count = 0
        today_data = fund_data_manager.get_ins().get_day_data(self.code,self.today)
        sub_count = 0
        if today_data != "sub":
            count += 1
            avg_price += today_data[1]
        while True:
            cur_time_stamp -= 3600 * 24
            last_day = time.localtime(cur_time_stamp)
            year = last_day[0]
            mon = last_day[1]
            day = last_day[2]
            last_key = "{0}-{1}-{2}".format(str(year).zfill(2),str(mon).zfill(2),str(day).zfill(2))
            last_data = fund_data_manager.get_ins().get_day_data(self.code,last_key)
            if last_data != "sub":
                count += 1
                avg_price += last_data[1]
                sub_count = 0
            else:
                sub_count +=1
                if sub_count > 10:
                    break

            if count >= max_day:
                break
        return avg_price/max_day

    def clear_buy_list(self):
        self.buy_list = []

    def cal_hold_avg_price(self):
        vol = 0
        money = 0
        for item in self.buy_list:
            vol += item[0]
            money += item[1]
        if vol == 0:
            return 0
        else:
            return money/vol

    def today_decision(self):
        avg_20 = self.cal_last_average(20)
        today_data = fund_data_manager.get_ins().get_day_data(self.code,self.today)
        cur_price = today_data[1]
        hold_price = self.cal_hold_avg_price()
        avg_60 = self.cal_last_average(60)
        #没有持股
        if self.hold_stock == 0:
            #突破二十日向上买入当前金额的对应风险数
            if avg_20 > 0 :
                if cur_price < avg_20 and cur_price > avg_60 :
                    self.buy(self.cur_money/(1/self.risk_per))
        else:
            
            if (self.hold_stock * cur_price + self.cur_money )/self.last_all_money < 1-self.risk_per :
                self.sell(self.hold_stock)
                return
            #止盈
            if cur_price / hold_price > 1 + self.risk_per*2:
                self.sell(self.hold_stock)
                return
            #突破二十日向下
            if cur_price < avg_20:
                #突破六十日向下
                if cur_price < avg_60:
                    if hold_price > cur_price and cur_price/hold_price < 1-self.risk_per:
                        per = min((1 - cur_price/avg_20)/self.risk_per,1)
                        self.sell(self.hold_stock * per)
                else:
                    #没有向下突破六十日均线向下
                    if cur_price > hold_price:
                        money = max((cur_price/hold_price - (1-self.risk_per)),0)/self.risk_per * self.cur_money
                        self.buy(money)
                        
            #突破二十日向上
            else:
                #突破六十日向上
                if cur_price > avg_60:
                    #持仓价格高于当前价格
                    last_buy_day = self.buy_list[-1][2]
                    cur_time_stamp = time.mktime(time.strptime(self.today,'%Y-%m-%d'))
                    last_time_stamp = time.mktime(time.strptime(last_buy_day,'%Y-%m-%d'))
                    if (cur_time_stamp - last_time_stamp) /(24 * 3600) > 5:
                        if hold_price > cur_price:
                            self.buy(self.cur_money * self.risk_per * 2)
                        else:
                            self.buy(self.cur_money * self.risk_per)
