
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
        record = []
        start_stamp = time.mktime(time.strptime(self.start_day,'%Y-%m-%d'))
        end_stamp = time.mktime(time.strptime(self.today,'%Y-%m-%d'))
        
        price_list = []
        date_list = []
        avg_list = []
        while True:
            if start_stamp > end_stamp:
                break
            struct = time.localtime(start_stamp)
            date = "{0}-{1}-{2}".format(str(struct[0]).zfill(2),str(struct[1]).zfill(2),str(struct[2]).zfill(2))
            data = fund_data_manager.get_ins().get_day_data(self.code,date)
            if data != "sub":
                price_list.append(data[1])
                date_list.append(date)
                avg_price = self.cal_last_average_start_date(20,date)
                avg_list.append(avg_price)
                
            start_stamp += 24 * 3600

        for item in self.record_list:
            record.append((item["date"],item["trading_price"],item["act"]))
        return {"record":record,"price":price_list,"date":date_list,"avg":avg_list}

    def on_end_simulation(self):
        hold_price = self.cal_hold_avg_price()
        last_trad_date = self.find_next_trad_day(self.today,dir = -1)
        today_data = fund_data_manager.get_ins().get_day_data(self.code,last_trad_date)

        if today_data != "sub":
            cur_price = today_data[1]
            all_money = self.hold_stock * cur_price + self.cur_money + self.today_trading_money + self.today_sell_vol * cur_price
            gain = all_money - self.start_money
            use = 0
            for item in self.record_list:
                if item["act"] == "BUY":
                    use += item['trading_vol'] * item['trading_price'] 
            
            gain_per = 0
            if use != 0 :
                gain_per = round(gain/use * 100,2)
            all_money = all_money
            date = self.find_next_trad_day(self.start_day,dir = -1)
            start_price = fund_data_manager.get_ins().get_day_data(self.code,date)[1]
            auto_per = round((cur_price-start_price)/start_price * 100,2)
            print(self.tag,self.today,self.code,"流动资金",self.cur_money + self.today_trading_money,"现价",cur_price,"持有份额",self.hold_stock,"持有价",hold_price,"总价值",all_money,"资金增长率",gain_per,"自然增长率",auto_per)
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
        

    def find_next_trad_day(self,start_date,end_date = -1,dir = 1):
        start_stamp = time.mktime(time.strptime(start_date,'%Y-%m-%d'))
        endday_stamp = None
        if end_date == -1:
            endday_stamp = start_stamp + dir * 24 * 3600 *30
        else:
            endday_stamp = time.mktime(time.strptime(end_date,'%Y-%m-%d'))
        cur_date = start_date
        start_data = fund_data_manager.get_ins().get_day_data(self.code,cur_date)
        if start_data != "sub":
            return cur_date
        while True:
            ret = self.cal_next_day(cur_date,dir)
            is_go = ret[0]
            cur_date = ret[1]
            if not is_go:
                return cur_date
            today_stamp = time.mktime(time.strptime(cur_date,'%Y-%m-%d'))
            if dir == 1 and today_stamp > endday_stamp:
                return None
            elif dir == -1 and today_stamp < endday_stamp:
                return None
    
    def cal_next_day(self,cur_date,dir):
        target_day = time.strptime(cur_date,'%Y-%m-%d')
        target_stamp = time.mktime(target_day)
        target_stamp+= 3600 * 24 * dir
        next_day = time.localtime(target_stamp)
        next_day = "{0}-{1}-{2}".format(str(next_day[0]).zfill(2),str(next_day[1]).zfill(2),str(next_day[2]).zfill(2))
        if fund_data_manager.get_ins().get_day_data(self.code,next_day) == "sub":
            return (True,next_day)
        else:
            return (False,next_day)

    def on_end_today(self,next_day):
        
        trad_day = self.find_next_trad_day(self.today,next_day,dir = 1)
        self.today = next_day
        trad_data = None
        if trad_day:
            trad_data = fund_data_manager.get_ins().get_day_data(self.code,trad_day)
        if trad_data:
            self.settlement(trad_data)
        self.today_decision()

    def settlement(self,trad_data):
        price = trad_data[1]
        if self.today_sell_vol != 0:
            money = price * self.today_sell_vol
            self.cur_money += money
            self.record_action("SELL",trad_data[0],self.today_sell_vol,price,self.temp_data['sell_reson'])
            del self.temp_data['sell_reson']
            self.sell_list.append([self.today_sell_vol,money,trad_data[0],price])
            self.trading_list.append([self.today_sell_vol,money,trad_data[0],price,"SELL"])
            self.today_sell_vol = 0
            if self.hold_stock == 0:
                self.clear_buy_list()
                self.last_money = self.cur_money  
        if self.today_trading_money != 0:
            vol = self.today_trading_money/price
            #计算份额
            self.hold_stock += vol
            self.record_action("BUY",trad_data[0],vol,price,self.temp_data['buy_reson'])
            del self.temp_data['buy_reson']
            self.buy_list.append([vol,self.today_trading_money,trad_data[0],price])
            self.trading_list.append([vol,self.today_trading_money,trad_data[0],price,"BUY"])
            self.today_trading_money = 0



    def record_action(self,act,trad_date,trading_vol,trading_price,reson = None):
        all_money = self.hold_stock * trading_price 
        act_record = {
            'date':trad_date,
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

    def cal_last_average_start_date(self,max_day,from_date):
        from_struct = time.strptime(from_date,'%Y-%m-%d')
        cur_time_stamp = time.mktime(from_struct)
        avg_price = 0
        count = 0
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

            if (cur_price - hold_price)/hold_price * 100 > self.sell_per + 10 and (cur_time_stamp - last_time_stamp) /(24*3600) > 5:
                self.sell_per += 10 
                self.sell(self.hold_stock * 0.2 ,"卖出20%")
                return;
            if (cur_price - hold_price)/hold_price * 100 > 20 :
                self.sell_per = 100
                self.sell(self.hold_stock ,"止盈")
                return;