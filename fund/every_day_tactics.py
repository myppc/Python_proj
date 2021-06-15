
from fund_data_manager import fund_data_manager
import time
import math
from db.db_loader_helper import db_loader
from tactics import base_tactics
from fund_data_manager import fund_data_manager
import fund_data_puller

class every_day_tactics(base_tactics):
    tag = "EVERY_DAY"
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

    def load_today(self):
        db = db_loader.get_ins().get_db("running_data_"+self.code)
        self.start_money = db.get_info("start_money")
        self.last_money = db.get_info("last_money")
        self.cur_money = db.get_info("cur_money")
        self.trading_list = db.get_info("trading_list")
        self.hold_stock = db.get_info("hold_stock")
        self.start_day = db.get_info("start_day")
        self.today = db.get_info("today")
        self.record_list = db.get_info("record_list")
        self.today_trading_money = db.get_info("today_trading_money")
        self.today_sell_vol = db.get_info("today_sell_vol")
        self.temp_data = db.get_info("temp_data")
        self.buy_list = db.get_info("buy_list")
        self.risk_per = db.get_info("risk_per")
        self.price_list = db.get_info("price_list")
        self.sell_per = db.get_info("sell_per")
        
    def save_today(self):
        db = db_loader.get_ins().get_db("running_data_"+self.code)
        db.set_info("start_money",self.start_money)
        db.set_info("trading_list",self.trading_list)
        db.set_info("cur_money",self.cur_money)
        db.set_info("hold_stock",self.hold_stock)
        db.set_info("last_money",self.last_money)
        db.set_info("start_day",self.start_day)
        db.set_info("today",self.today)
        db.set_info("record_list",self.record_list)
        db.set_info("today_trading_money",self.today_trading_money)
        db.set_info("today_sell_vol",self.today_sell_vol)
        db.set_info("temp_data",self.temp_data )
        db.set_info("buy_list",self.buy_list)
        db.set_info("risk_per",self.risk_per)
        db.set_info("price_list",self.price_list)
        db.set_info("sell_per",self.sell_per)
        db.flush()

    def update_db_data(self):
        fund_data_puller.update(self.code)

    def today_decision(self):
        cur_time = time.localtime()
        # if cur_time[3] > 14:
        #     print("今日买卖时间已经结束，不能再进行交易")
        #     return
        basis_day = self.find_next_trad_day(self.today,end_date = -1,dir = -1)
        basis_data = fund_data_manager.get_ins().get_day_data(self.code,basis_day)
        if basis_data == "sub":
            return
        cur_price = basis_data[1] #当前价格
        hold_price = self.cal_hold_avg_price()#持有成本价格
        last_price = self.find_last_limit_price(20)
        avg10 = self.cal_last_average(10)
        min_20 = last_price[0]
        max_20 = last_price[1]
        

        if self.hold_stock ==0 : 
            if cur_price > max_20:
                print(basis_day,"BUY","突破二十日最大值,当前价格",cur_price,"20日最高价",max_20,"买入",round(self.last_money  * 0.25,2),"(Y/N)?")
                if input() == "y":
                    self.buy(self.last_money  * 0.25,"突破二十日最大值")
                return
        else:
            last_buy_day = self.trading_list[-1][2]
            cur_time_stamp = time.mktime(time.strptime(basis_day,'%Y-%m-%d'))
            last_time_stamp = time.mktime(time.strptime(last_buy_day,'%Y-%m-%d'))
            if (avg10 - cur_price)/avg10 > 0.05 and (cur_time_stamp - last_time_stamp) /(24*3600) > 5:
                self.sell_per -= 10
                self.sell_per = max(self.sell_per,100)
                print(basis_day,"BUY","补仓,当前价格",cur_price,"10日均价",avg10,"买入",round(self.cur_money  * 0.25,2),"(Y/N)?")
                if input() == "y":
                    self.buy(self.cur_money  * 0.1,"补仓")
                return;

            if (cur_price - hold_price)/hold_price * 100 > self.sell_per + 10 and (cur_time_stamp - last_time_stamp) /(24*3600) > 5:
                self.sell_per += 10 
                print(basis_day,"SELL","触发卖出点",cur_price,"持仓价",hold_price,"卖出",round(self.hold_stock  * 0.2,2),"(Y/N)?")
                if input() == "y":
                    self.sell(self.hold_stock * 0.2 ,"卖出20%")
                return;
            if (cur_price - hold_price)/hold_price * 100 > 20 :
                self.sell_per = 100
                print(basis_day,"SELL","触发止盈点",cur_price,"持仓价",hold_price,"卖出",round(self.hold_stock,2),"(Y/N)?")
                if input() == "y":
                    self.sell(self.hold_stock ,"止盈")
                return;
        print(self.today ,"没有任何操作")