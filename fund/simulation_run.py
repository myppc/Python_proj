from simulation_market import simulation_market
from fund_data_manager import fund_data_manager
from code_config import code_list
from db.db_loader_helper import db_loader
import fund_filter
import time
import re


def main():
	act = input("1.执行今日操作\n2.进行数据模拟\n 3.拉取全部基金列表\n4.拉取指定基金数据\n5.进行当前数据排名\n6.修复拉取忽略列表\n")
	if act == "1":
		for code in code_list:
			market = simulation_market()
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
		fund_data_manager.get_ins().check_out_all_fund_code()
	elif act == "4":
		fund_data_manager.get_ins().check_out_fund_base_data()
	elif act == "5":
		fund_filter.rank_fund_base_data()
	elif act == "6":
		db = db_loader.get_ins().load_db("fund_base_data")
		code_list_cur = db.get_all_keys()
		ignore_db = db_loader.get_ins().load_db("ignore_base_data_pull_list")
		ignore_db.set_info("ignore_list",code_list_cur)
	db_loader.get_ins().close()

main()

