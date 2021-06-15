import spider
import sys
import time
import math

from db.db_loader_helper import db_loader

fund_data_manager_instance = None

class fund_data_manager:
	def get_ins():
		global fund_data_manager_instance
		if not fund_data_manager_instance:
			fund_data_manager_instance = fund_data_manager()
		return fund_data_manager_instance

	def __init__(self):
		pass


	def set_history_data(self,code,server_data):
		db = db_loader.get_ins().load_db(code)
		for item in server_data:
			key = item[0]
			db.set_info(key,item)
		db.flush()

	def get_day_data(self,code,day):
		db = db_loader.get_ins().load_db(code)
		data = db.get_info(day)
		if not data:
			db.set_info(day,"sub")
			return "sub"
		else:
			if data != "sub":
				data[1] = float(data[1])
				data[2] = float(data[2])
			return data

	def cal_taget_page(self,day):
		cur_time = time.localtime()
		year = cur_time[0]
		mon = cur_time[1]
		today = cur_time[2]
		today = time.strptime("{0}-{1}-{2}".format(year, mon,today),'%Y-%m-%d')
		today_stamp = time.mktime(today)
		target_day = time.strptime(day,'%Y-%m-%d')
		target_stamp = time.mktime(target_day)
		dis_day = (today_stamp - target_stamp)/(3600 * 24)
		total = dis_day + 6-today[6]
		total = total + target_day[6] + 1
		dis_day = dis_day - math.ceil(dis_day*13/360)
		sub_day = total/7*2
		sub_day -= min(6-today[6],2)
		sub_day -= max(2 + target_day[6] - 6,0)
		page = math.ceil((dis_day - sub_day)/20)
		ret = [max(1,page - 1),page + 1]
		return ret

	def pull_cur_to_target_day(self,code,day):
		max_page = self.cal_taget_page(day)[1]
		server_data = spider.catch_code_history(code,max_page)
		self.set_history_data(code,server_data)
		today_struct = time.localtime()
		today_date = "{0}-{1}-{2}".format(str(today_struct[0]).zfill(2),str(today_struct[1]).zfill(2),str(today_struct[2]).zfill(2))
		self.save_pull_date(code,today_date)

	def check_fund_data_exist(self,code):
		return db_loader.get_ins().check_db_exist(code)

	def save_pull_date(self,code,date):
		pull_record_db = db_loader.get_ins().load_db("pull_record")
		pull_record_db.set_info(code,date)
	
	def check_today_need_pull(self,code):
		pull_record_db = db_loader.get_ins().load_db("pull_record")
		date = pull_record_db.get_info(code)
		if date == None :
			return True
		else:
			today_struct = time.localtime()
			today_date = "{0}-{1}-{2}".format(str(today_struct[0]).zfill(2),str(today_struct[1]).zfill(2),str(today_struct[2]).zfill(2))
			today_stamp = time.mktime(time.strptime(today_date,'%Y-%m-%d'))
			last_stamp = time.mktime(time.strptime(date,'%Y-%m-%d'))
			return today_stamp > last_stamp
		
