
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

    def __init__(self,start_money = "",start_day = "",code = ""):
        self.cur_money = start_money
        self.last_money = start_money
        self.start_money = start_money
        self.start_day = start_day
        self.today = start_day
        self.code = code
        self.temp_data = {}
        self.buy_list = [] #零时记录购买价格
        self.sell_list = []
        self.trading_list = []
        self.price_list = [] #每日交易价格
        self.start_price = None
        self.sell_per = 100


    def find_last_limit_price(self,max_day):
        today = time.strptime(self.today,'%Y-%m-%d')
        cur_time_stamp = time.mktime(today)
        count = 0
        today_data = fund_data_manager.get_ins().get_day_data(self.code,self.today)
        min_price = 99999
        max_price = 0
        sub_count = 0
        while True:
            cur_time_stamp -= 3600 * 24
            last_day = time.localtime(cur_time_stamp)
            year = last_day[0]
            mon = last_day[1]
            day = last_day[2]
            last_key = "{0}-{1}-{2}".format(str(year).zfill(2),str(mon).zfill(2),str(day).zfill(2))
            last_data = fund_data_manager.get_ins().get_day_data(self.code,last_key)
            if last_data != "sub":
                sub_count = 0
                count += 1
                max_price = max(last_data[1],max_price)
                min_price = min(last_data[1],min_price)
            else:
                sub_count +=1
                if sub_count > 10:
                    break
            if count >= max_day:
                break
        return (min_price,max_price)

    def save_result(self):
        f = open(".\\result\\simulation_"+self.tag+"_"+str(self.code)+".txt","w+",encoding = "UTF-8")
        msg = ""
        for info in self.record_list:
            msg = msg + json.dumps(info,ensure_ascii=False) +"\n"
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
        all_money = self.hold_stock * cur_price + self.cur_money + self.today_trading_money + self.today_sell_vol * cur_price
        auto_per = round(cur_price/self.start_price * 100,2)
        money_per = round(all_money/self.start_money * 100,2)
        print(self.tag,self.today,self.code,"流动资金",self.cur_money + self.today_trading_money,"现价",cur_price,"持有份额",self.hold_stock,"持有价",hold_price,"总价值",all_money,"资金增长率",money_per,"自然增长率",auto_per)
        self.save_result()

    def buy(self,money,reson = None):
        money = min(self.cur_money , money)
        money = math.floor(money)
        if money < 10:
            return 
        self.cur_money = self.cur_money - money
        self.today_trading_money = money
        self.temp_data['buy_reson'] = reson

    def sell(self,stock_vol,reson = None):
        stock_vol = math.floor(stock_vol)
        stock_vol = min(self.hold_stock , stock_vol)
        self.hold_stock = self.hold_stock - stock_vol
        self.today_sell_vol = stock_vol
        if self.hold_stock < 1:
            self.today_sell_vol += self.hold_stock
            self.hold_stock = 0
        self.temp_data['sell_reson'] = reson
        

    def on_end_today(self,next_day):
        today_data = fund_data_manager.get_ins().get_day_data(self.code,self.today)
        if today_data != "sub":
            self.settlement(today_data)
            self.today_decision()
            self.today = next_day
            if self.start_price == None:
                self.start_price = today_data[1]

    def settlement(self,today_data):
        price = today_data[1]
        self.price_list.append((price,self.today))
        if self.today_sell_vol != 0:
            money = price * self.today_sell_vol
            self.cur_money += money
            self.record_action("SELL",self.today_sell_vol,price,self.temp_data['sell_reson'])
            del self.temp_data['sell_reson']
            self.sell_list.append([self.today_sell_vol,money,self.today,price])
            self.trading_list.append([self.today_sell_vol,money,self.today,price,"SELL"])
            self.today_sell_vol = 0
            if self.hold_stock == 0:
                self.clear_buy_list()
                self.last_money = self.cur_money  
        if self.today_trading_money != 0:
            vol = self.today_trading_money/price
            #计算份额
            self.hold_stock += vol
            self.record_action("BUY",vol,price,self.temp_data['buy_reson'])
            del self.temp_data['buy_reson']
            self.buy_list.append([vol,self.today_trading_money,self.today,price])
            self.trading_list.append([vol,self.today_trading_money,self.today,price,"BUY"])
            self.today_trading_money = 0



    def record_action(self,act,trading_vol,trading_price,reson = None):
        all_money = self.hold_stock * trading_price 
        act_record = {
            'date':self.today,
            'act':act,
            'trading_vol':trading_vol,
            'hold_stock':self.hold_stock,
            'trading_price':trading_price,
            'cur_money':self.cur_money,
            'all_money':all_money + self.cur_money,
            'index':len(self.price_list),
            'reson':reson}
        print(self.today,act,"交易价",trading_price,"交易金额",math.floor(trading_vol * trading_price),"交易量",math.floor(trading_vol),"持有量",math.floor(self.hold_stock),"总价值",math.floor(all_money + self.cur_money),reson)
        self.record_list.append(act_record)

    def cal_last_average(self,max_day,before = 0):
        today = time.strptime(self.today,'%Y-%m-%d')
        cur_time_stamp = time.mktime(today)
        cur_time_stamp -= 3600 * 24 * before
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
        return avg_price/count

    def clear_buy_list(self):
        self.buy_list = []
        self.trading_list = []

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

    def cal_atr(self,max_day):
        today = time.strptime(self.today,'%Y-%m-%d')
        cur_time_stamp = time.mktime(today)
        count = 0
        today_data = fund_data_manager.get_ins().get_day_data(self.code,self.today)
        price_list = []
        sub_count = 0
        avg_price = self.cal_last_average(20)
        while True:
            cur_time_stamp -= 3600 * 24
            last_day = time.localtime(cur_time_stamp)
            year = last_day[0]
            mon = last_day[1]
            day = last_day[2]
            last_key = "{0}-{1}-{2}".format(str(year).zfill(2),str(mon).zfill(2),str(day).zfill(2))
            last_data = fund_data_manager.get_ins().get_day_data(self.code,last_key)
            if last_data != "sub":
                sub_count = 0
                count += 1
                price_list.append(last_data[1])
            else:
                sub_count +=1
                if sub_count > 10:
                    break
            if count >= max_day:
                break
        all_tr = 0
        for item in price_list:
            all_tr += abs(item - avg_price)
        if len(price_list):
            return all_tr/len(price_list)
        else:
            return 0


    def today_decision(self):
        today_data = fund_data_manager.get_ins().get_day_data(self.code,self.today)
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

            if (cur_price - hold_price)/hold_price * 100 > self.sell_per + 10 and (cur_time_stamp - last_time_stamp) /(24*3600) > 5:
                self.sell_per += 10 
                self.sell(self.hold_stock * 0.2 ,"卖出20%")
                return;
            if (cur_price - hold_price)/hold_price * 100 > 20 :
                self.sell_per = 100
                self.sell(self.hold_stock ,"止盈")
                return;