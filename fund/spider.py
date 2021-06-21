from selenium import webdriver

from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from threading import Thread,Lock
import os
import time
from selenium.webdriver.common.by import By
import pandas as pd
import json
from db.db_loader_helper import db_loader
import re
import random
# 下面是利用 selenium 抓取html页面的代码
# 初始化函数
def pull_page_count(fund_url,driver):
    driver.get(fund_url)
    getPage_text = driver.find_element_by_id("pagebar").find_element_by_xpath("div[@class='pagebtns']/label[text()='下一页']/preceding-sibling::label[1]").get_attribute("innerHTML")
    total_page = int("".join(filter(str.isdigit, getPage_text)))
    return total_page

def getData(myrange,driver,lock,code,ret_list,total):
    for x in myrange:
        lock.acquire()
        jjcode = code
        tonum = driver.find_element_by_id("pagebar").find_element_by_xpath("div[@class='pagebtns']/input[@class='pnum']")
        jumpbtn = driver.find_element_by_id("pagebar").find_element_by_xpath("div[@class='pagebtns']/input[@class='pgo']")
        tonum.clear()
        tonum.send_keys(str(x))
        jumpbtn.click()
        time.sleep(1)
        WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_id("pagebar").find_element_by_xpath("div[@class='pagebtns']/label[@value={0} and @class='cur']".format(x)) != None)
        table = driver.find_element_by_xpath("//table[@class='w782 comm lsjz']/tbody")
        for row in table.find_elements_by_xpath(".//tr"):
            col = row.find_elements(By.TAG_NAME, "td")
            #日期 
            colum0 = col[0].text
            #当前价格
            colum1 = col[1].text
            colum1 = colum1.replace("*","")
            colum2 = col[2].text
            if colum2=='':
                colum2 = colum1
            #比率
            colum3 = col[3].text
            colum3 = colum3.replace("%","")
            item = [colum0,colum1,colum2,colum3]
            ret_list.append(item)
            print("...finish " ,colum0)
        lock.release() 
        
# 开始抓取函数
def catch_code_history(code,history_page_max):
    driver = webdriver.PhantomJS(executable_path=r"C:\\Users\\myppc\\Desktop\\hzy\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe")
    code = str(code).zfill(6)
    fund_url='http://fund.eastmoney.com/f10/jjjz_'+code +'.html'
    total_page = pull_page_count(fund_url,driver)
    lock = Lock()
    if history_page_max == -1:
        history_page_max = total_page
    if total_page >history_page_max:
        total_page = history_page_max
    r = range(1, int(total_page)+1)
    step = 10
    range_list = [r[x:x + step] for x in range(0,len(r),step)]
    thread_list = []
    ret_list = []
    for r in range_list:
        t = Thread(target=getData, args=(r,driver,lock,code,ret_list,total_page))
        thread_list.append(t)
        t.start()
    for t in thread_list:
        t.join()
    sort_list = sort_server_data(ret_list)
    return sort_list

# 抓取指定页数
def catch_page_history(code,page_around):
    driver = webdriver.PhantomJS(executable_path=r"C:\\Users\\myppc\\Desktop\\hzy\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe")
    code = str(code).zfill(6)
    fund_url='http://fund.eastmoney.com/f10/jjjz_'+code +'.html'
    total_page = pull_page_count(fund_url,driver)
    page_min = page_around[0]
    page_max = page_around[1]
    if page_max > total_page:
        page_max = total_page
    page_range = range(page_min,page_max)
    print(page_range)
    lock = Lock()
    ret_list = []
    t = Thread(target=getData, args=(page_range,driver,lock,code,ret_list))
    t.start()
    t.join()
    sort_list = sort_server_data(ret_list)
    return sort_list

def sort_server_data(server_data):
    sort_list = []
    for item in server_data:
        timestamp = time.mktime(time.strptime(item[0], "%Y-%m-%d"))
        item.insert(0,timestamp)
        is_insert = True
        for index in range(0,len(sort_list)):
            if sort_list[index][0] > timestamp:
                is_insert = False
                sort_list.insert(index,item)
                break
        if is_insert :
            sort_list.append(item)
    for item in sort_list:
        del item[0]
    return server_data

def catch_all_fund_list():
    url = 'http://fund.eastmoney.com/js/fundcode_search.js'
    driver = webdriver.PhantomJS(executable_path=r"C:\\Users\\myppc\\Desktop\\hzy\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe")
    driver.get(url)
    element = driver.find_element(By.XPATH,"//pre[contains(text(),'var')]")
    text = element.text
    pos = text.find("[")
    json_str = text[pos:-1]
    data_list = json.loads(json_str)
    return data_list

def catch_fund_base_data(code_list):
    db = db_loader.get_ins().load_db("fund_base_data")
    ignore_db = db_loader.get_ins().load_db("ignore_base_data_pull_list")
    ignore_list = ignore_db.get_info("ignore_list") or []
    base_url = 'http://fund.eastmoney.com/{0}.html?spm=001.1.swh'
    sharpe_url = 'http://fundf10.eastmoney.com/tsdata_{0}.html'
    driver = webdriver.PhantomJS(executable_path=r"C:\\Users\\myppc\\Desktop\\hzy\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe")
    for code in code_list:
        if code in ignore_list:
            continue
        info = {}

        try:
            url = base_url.format(code)
            driver.get(url)
            body_element = driver.find_element_by_xpath("//div[@id='body']").find_element_by_xpath("//div[@class='quotationItem_left quotationItem_left02']")
            gain_element = body_element.find_element_by_xpath("//div[@id='IncreaseAmount']").find_element_by_xpath("//li[@id='increaseAmount_stage']")
            gain_text = gain_element.text
            
            gain_text_list = re.split("阶段涨幅\n|同类平均\n|沪深300\n|跟踪标的\n|同类排名\n|四分位排名\n",gain_text)[1:]
            if "跟踪标的\n" in gain_text:
                del gain_text_list[3]
            name_list = ["stage_rate","same_avg","hs_300","same_rank","rank4"]
            index = 0
            for item in gain_text_list:
                name = name_list[index]
                info[name] = item.split("\n")
                index +=1 
            db.set_info(code,info)
            print("succ stage1 " ,code)
        except BaseException:
            print("check out error 1 " ,code)
            db.flush()
        time.sleep(round(random.uniform(0.5,2.5),2))

        try:
            url = sharpe_url.format(code)
            driver.get(url)
            sharpe_element = driver.find_element_by_xpath("//div[@class='boxitem w790']").find_element_by_xpath("//table[@class='fxtb']")
            sharpe_text = sharpe_element.text
            sharpe_text_list = re.split("\n标准差 |\n夏普比率 |\n信息比率",sharpe_text)[1:]
            if "\n信息比率" in sharpe_text:
                del sharpe_text_list[2]
            name_list = ["standard_dev","sharpe_rate"]
            index = 0
            for item in sharpe_text_list:
                name = name_list[index]
                info[name] = item.split(" ")
                index +=1 
            db.set_info(code,info)
            print("succ stage2 " ,code)
        except BaseException:
            print("check out error 2 " ,code)
            db.flush()
        ignore_list.append(code)
        ignore_db.set_info("ignore_list",ignore_list)
        time.sleep(round(random.uniform(0.5,2.5),2))
    db.flush()
    ignore_db.flush()