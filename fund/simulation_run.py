from simulation_market import simulation_market
from fund_data_manager import fund_data_manager
from code_config import code_list
from db.db_loader_helper import db_loader
import time


def main():
    act = input("1.执行今日操作，2.进行数据模拟 ,3.拉取全部基金列表 (1/2/3)? ")
    if act == "1":
        market = simulation_market()
        for code in code_list:
            market.code = code
            market.handel_today()
    elif act == "2":
        market = simulation_market()
        code = input("fund code = ")
        start_day = input("start date = ")
        end_day = input("end date = ")
        start_money = int(input("start money = "))
        market.auto_running(code,start_day,end_day,start_money)
    elif act == "3":
        fund_data_manager.get_ins().flush_all_fund_code()
    db_loader.get_ins().close()

main()

