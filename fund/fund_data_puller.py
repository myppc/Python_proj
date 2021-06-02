from fund_data_manager import fund_data_manager
from db.db_loader_helper import db_loader
import time

def main():
    act = str(input(" update or check out ?  (1/2) "))
    code = str(input("input code = "))
    if act == "2":
        if db_loader.get_ins().check_db_exist(code):
            go = input("this code data is exist ! go on ? y/n ")
            if go == "y":
                update(code)
                return
            elif go == "n":
                print("cancel CHECK OUT")
                return
        else:
            check_out(code)
            return 
    elif act == "1":
        if db_loader.get_ins().check_db_exist(code):
            update(code)
            return
        else:
            check_out(code)
            return

def update(code):
    cur_time = time.localtime() 
    year = cur_time[0]
    mon = cur_time[1]
    day = cur_time[2]
    today_str = "{0}-{1}-{2}".format(str(year).zfill(2), str(mon).zfill(2),str(day).zfill(2))
    today_struct = time.strptime(today_str,'%Y-%m-%d')
    today_stamp = time.mktime(today_struct)
    target_day = None
    while True:
        time_struct = time.localtime(today_stamp) 
        year = time_struct[0]
        mon = time_struct[1]
        day = time_struct[2]
        day_str = "{0}-{1}-{2}".format(str(year).zfill(2), str(mon).zfill(2),str(day).zfill(2))
        if fund_data_manager.get_ins().get_day_data(code,day_str) != "sub":
            target_day = day_str
            break
        else:
            today_stamp -= 24 * 3600
    if target_day:
        if target_day == today_str:
            print("data is already up to date")
        else:
            print("update to ",target_day)
            fund_data_manager.get_ins().pull_cur_to_target_day(code,target_day)
            print("update finish !")

def check_out(code):
    date = input("input date = ")
    print(code,date,"START CHECK OUT ?(y/n)")
    go = input()
    if go == "y":
        fund_data_manager.get_ins().pull_cur_to_target_day(str(code),date)
        print("check out finish !")
    else: 
        print("cancel CHECK OUT")

main()
