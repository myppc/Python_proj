from db.db_loader_helper import db_loader
from pandas import DataFrame;
import numpy as np
import csv

cost_list = {
    "rank4":[1,1,2,2,0,2,2,2],
    "sharpe":[5,10,15],
    "standard":[5,10,15],
    "same":[1,2,2,4,0,3,3,3],
    "stage":[1,2,2,2.5,0,2.5,2.5,2.5,0]
    }

fix_list = {
    "rank4":2,
    "sharpe":5,
    "standard":1,
    "same":1,
    "stage":1
}

def rank_fund_base_data():
    db = db_loader.get_ins().load_db("fund_base_data")
    fund_list_db = db_loader.get_ins().load_db("fund_list")
    key_list = db.get_all_keys()
    filter_list = []
    filter_type = ["股票型","指数型"]
    for key in key_list:
        if not fund_list_db.get_info(key)[3] in filter_type:
            continue
        dic = db.get_info(key)
        filter1 = False or "sharpe_rate" in dic
        filter2 = False or "standard_dev" in dic
        filter3 = False or "rank4" in dic
        filter4 = False or "same_rank" in dic
        filter5 = False or "stage_rate" in dic
        filter6 = False or "same_avg" in dic
        filter7 = False or "hs_300" in dic
        if filter1 and filter2 and filter3 and filter4 and filter5 and filter6 and filter7:
            filter_list.append(key)
    score_list = []
    for code in filter_list:
        item = filter_code(code)
        score_list.append(item)
    
    sort_list = []
    for item in score_list:
        is_insert = True
        for index in range(0,len(sort_list)):
            if sort_list[index][1] < item[1]:
                is_insert = False
                sort_list.insert(index,item)
                break
        if is_insert :
            sort_list.append(item)
    
    f = open('fund_rank.csv',"w",encoding='utf-8-sig',newline='')
    csv_writer = csv.writer(f)
    csv_writer.writerow(["代码","基金名","四分位","夏普率","标准差","同类排名","阶段涨幅","总分"])
    fund_db = db_loader.get_ins().load_db("fund_list")
    for item in sort_list:
        code = item[0] 
        name = fund_db.get_info(code)[2]
        score_list = item[2]
        all_score = item[1]
        rank4 = score_list[0]
        sharpe = score_list[1]
        standard = score_list[2]
        same = score_list[3]
        stage = score_list[4]
        csv_writer.writerow([code,name,rank4,sharpe,standard,same,stage,all_score])
    f.close()
    
def filter_stage_rate(stage_rate,same_avg,hs_300):
    _stage_rate = []
    _same_avg = []
    _hs_300 = []
    for index in range(len(stage_rate)):
        stage = stage_rate[index]
        same = same_avg[index]
        hs = hs_300[index]
        if stage.strip()  == "--" or stage.strip()  == "":
            stage = "0%"
        if same.strip()  == "--" or same.strip()  == "":
            same = "0%"
        if hs.strip()  == "--" or hs.strip()  == "":
            hs = "0%"
        _stage_rate.append(stage)
        _same_avg.append(same)
        _hs_300.append(hs)
    df_stage = DataFrame({'p_str':_stage_rate});
    stage_ret = df_stage['p_str'].str.strip("%").astype(float)/100;
    stage_ret = stage_ret.values.tolist()
    df_same = DataFrame({'p_str':_same_avg});
    same_ret = df_same['p_str'].str.strip("%").astype(float)/100;
    same_ret = same_ret.values.tolist()
    df_hs = DataFrame({'p_str':_hs_300});
    hs_ret = df_hs['p_str'].str.strip("%").astype(float)/100;
    hs_ret = hs_ret.values.tolist()
    return (stage_ret,same_ret,hs_ret)

def filter_rank(same_rank):
    same_rank = same_rank[:-1]
    ret = []
    for item in same_rank:
        if item == "":
            continue
        split = item.split("|")
        rank = 0
        if split[0].strip()  != "--" :
            rank = int(split[0])
        if split[1].strip() == "--" :
            ret.append(0)
            continue
        total = int(split[1])
        rank_per = 1 - rank/total * 1
        ret.append(rank_per)
    return ret

def filter_standard_dev(standard_dev):
    ret = []
    p_str_list = []
    for item in standard_dev:
        if item.strip()  == "--":
            item = '0%'
        p_str_list.append(item)
    df = DataFrame({'p_str':p_str_list});
    ret = df['p_str'].str.strip("%").astype(float)/100;
    ret = ret.values.tolist()
    return ret

def filter_sharpe_rate(sharpe_rate):
    ret = []
    p_str_list = []
    for item in sharpe_rate:
        if item.strip()  == "--":
            item = '0%'
        p_str_list.append(item)
    df = DataFrame({'p_str':p_str_list});
    ret = df['p_str'].str.strip("%").astype(float)/100;
    ret = ret.values.tolist()
    return ret

def filter_rank4(rank4):
    ret = []
    for item in rank4:
        if item == "优秀":
            ret.append(0.4)
            continue
        if item == "良好":
            ret.append(0.3)
            continue
        if item == "一般":
            ret.append(0.2)
            continue
        if item == "不佳":
            ret.append(0.1)
            continue
        if item.strip()  == "--":
            ret.append(0)
            continue
    return ret

def filter_code(code):
    print(code)
    db = db_loader.get_ins().load_db("fund_base_data")
    dic = db.get_info(code)
    rank4 = filter_rank4(dic["rank4"])
    sharpe = filter_sharpe_rate(dic["sharpe_rate"])
    standard = filter_standard_dev(dic["standard_dev"])
    same = filter_rank(dic["same_rank"])
    ret = filter_stage_rate(dic["stage_rate"],dic["same_avg"],dic["hs_300"])
    stage = ret[0]
    samve_avg = ret[1]
    hs = ret[2]

    nrank4 = np.array(rank4)
    nsharpe = np.array(sharpe)
    nstandard = np.array(standard)
    nsame = np.array(same)
    nstage = np.array(stage)
    nsame_avg = np.array(samve_avg)
    nhs = np.array(hs)
    nstage = nstage - nsame_avg + (nstage - nhs)
    score = 0
    data = {
        "rank4":nrank4,
        "sharpe":nsharpe,
        "standard":nstandard,
        "same":nsame,
        "stage":nstage,
    }
    score_list = []
    for key in data:
        arg1 = data[key]
        arg2 = cost_list[key]
        cur_score = np.multiply(arg1,arg2).sum() * fix_list[key]
        score += cur_score
        score_list.append(round(cur_score,3))

    return (code,score,score_list)

def test():
    db = db_loader.get_ins().load_db("fund_list")
    info = db.get_info("004698")
    print(info)
