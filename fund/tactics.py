
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
        self.start_money = start_money
        self.start_day = start_day
        self.today = start_day
        self.code = code
        self.temp_data = {}
        self.buy_list = [] #零时记录购买价格
        self.sell_list = []
        self.price_list = [] #每日交易价格
        self.max_price = None
        self.min_price = None

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
        all_money = self.hold_stock * cur_price + self.cur_money
        print(self.tag,self.today,self.code,"cur_money",self.cur_money,"cur_pric",cur_price,"hold_stock",self.hold_stock,"hold_price",hold_price,"all_money",all_money)
        self.save_result()

    def buy(self,money,reson = None):
        if len(self.buy_list) != 0:
            info = self.buy_list[-1]
            date = info[2]
            last_price = info[3]
            avg20 = self.cal_last_average(20)
            cur_time_stamp = time.mktime(time.strptime(self.today,'%Y-%m-%d'))
            last_time_stamp = time.mktime(time.strptime(date,'%Y-%m-%d'))
            if abs(last_price - avg20)/avg20 *100 < 5  and (cur_time_stamp - last_time_stamp)/(24 * 3600) < 5:
                return
        money = min(self.cur_money , money)
        money = math.floor(money)
        if money < 10:
            return 
        self.cur_money = self.cur_money - money
        self.today_trading_money = money
        self.temp_data['buy_reson'] = reson

    def sell(self,stock_vol,reson = None):
        if len(self.sell_list) != 0:
            info = self.sell_list[-1]
            date = info[2]
            last_price = info[3]
            avg20 = self.cal_last_average(20)
            cur_time_stamp = time.mktime(time.strptime(self.today,'%Y-%m-%d'))
            last_time_stamp = time.mktime(time.strptime(date,'%Y-%m-%d'))
            if abs(last_price - avg20)/avg20*100 < 5  and (cur_time_stamp - last_time_stamp)/(24 * 3600) < 5:
                return
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

    def settlement(self,today_data):
        price = today_data[1]
        if not self.max_price:
            self.max_price = price
        if not self.min_price:
            self.min_price = price
        self.max_price = max(price,self.max_price)
        self.min_price = min(price,self.min_price)
        self.price_list.append(price)
        if self.today_sell_vol != 0:
            money = price * self.today_sell_vol
            self.cur_money += money
            self.record_action("SELL",self.today_sell_vol,price,self.temp_data['sell_reson'])
            del self.temp_data['sell_reson']
            self.sell_list.append([self.today_sell_vol,money,self.today,price])
            self.today_sell_vol = 0
            if self.hold_stock == 0:
                self.clear_buy_list()        
        if self.today_trading_money != 0:
            vol = self.today_trading_money/price
            #计算份额
            self.hold_stock += vol
            self.record_action("BUY",vol,price,self.temp_data['buy_reson'])
            del self.temp_data['buy_reson']
            self.buy_list.append([vol,self.today_trading_money,self.today,price])
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
        
        today_data = fund_data_manager.get_ins().get_day_data(self.code,self.today)
        cur_price = today_data[1] #当前价格
        hold_price = self.cal_hold_avg_price()#持有成本价格
        avgb60_10 = self.cal_last_average(10,60)#六十日前二十日均价
        avgb40_10 = self.cal_last_average(10,40)#四十日前二十日均价
        avgb20_10 = self.cal_last_average(10,20)#二十日前二十日均价
        avgb10_10 = self.cal_last_average(10,10)#十日前二十日均价
        avgb5_10 = self.cal_last_average(10,5)#五日前二十日均价
        avg_5 = self.cal_last_average(5)#最近五日平均价格
        avg_20 = self.cal_last_average(20)#最近二十日平均价格
        avg_10 = self.cal_last_average(10)#最近十日平均价格
        d10_5 = (avgb5_10 - avgb10_10)/(10 -5) * 1000
        d5_0 = (avg_10 - avgb5_10)/5 * 1000

        if avg_5 > avg_20 and avgb60_10 > avgb40_10 and avgb40_10 >avgb20_10 and abs(avgb20_10 - avg_20)/avgb20_10*100 < 5 :
            self.buy(self.cur_money * self.risk_per,"买入点1")
            return
        #5日前均价与今日均价距离没有拉开，且40日前开始出现下跌，现在出现低谷攀升
        if abs(avgb10_10 - avg_20)/avgb20_10 * 100 < 5 and avgb40_10 > avgb20_10 and avgb20_10 > avgb10_10 and d5_0 > 0:
            self.buy(self.cur_money * self.risk_per,"出现低谷攀升")
            return 

        if self.min_price:
            if abs(cur_price - self.min_price)/self.min_price * 100 < 5 and cur_price > self.min_price :
                self.buy(self.cur_money * self.risk_per,"历史最低价附近")
                return

        if self.max_price:
            if self.today == "2020-07-30":
                print(abs(avg_20 - self.max_price)/self.max_price * 100,avg_10,avgb5_10,d5_0)
            if abs(avg_20 - self.max_price)/self.max_price * 100 < 5 and d5_0 < 0 :
                self.sell(self.hold_stock * self.risk_per,"历史最高价附近，且开始下跌")
                return

        if self.hold_stock != 0 : 
            if cur_price/hold_price > 1+ 2*self.risk_per and d5_0 > 0:
                self.sell(self.hold_stock,"止盈，全部卖出")
                return 
 
