import os
import re
import config as config
import ignore as ignore
import white as white
import auto_target 

lua_path = config.project_path + config.lua_path
save_path = config.save_path
cn_path = config.project_path + config.cn_config_path

dic = {}
array = []
target_dic = {}
replace_dic = {}
cn_dic = {}

file_count = 0

input_list = ["y","n","over"]


# lua路径
def format_u3d_asset(path, ex_path):
    # 遍历所有文件
    files = os.listdir(path)
    for f in files:
        fi_d = os.path.join(lua_path, ex_path, f)
        # 是文件
        if not os.path.isdir(fi_d):
            # 是否是lua代码
            if f.lower().endswith(('.lua')):
                if not f in ignore.ignore_list:
                    check_lua(fi_d, f)
        else:
            format_u3d_asset(fi_d, os.path.join(ex_path, f))


# 检测lua
def check_lua(path, filename):
    file = open(path, encoding="utf-8")
    isHas = False
    file_array = []
    count = 0
    
    while 1:
      line = file.readline()
      if not line:
        break
      count = count + 1
      line = line.strip()
      
      if not line.startswith("ULog") and check_line(line, count, file_array,filename,path):
        isHas = True

    if isHas:
        global file_count
        file_count = file_count + 1
        array.extend(["=================================", filename + ":"])
        array.extend(file_array)
      
    file.close()


# 判断行
def check_line(line, line_count, file_array,filename,path):
    isHas = False

    quo_str = None # 开头的引号
    last_char = None
    
    content = ""
    
    for c in line:
        # 是否在引号中
        if quo_str != None:
            # 是否是相同引号且之前不是转义
            if c == quo_str and last_char != '\\':
                add = ""
                if quo_str == "'":
                    add = '\"'
                else:
                    add = '\"'
                quo_str = None
                
                # 引号内判断
                if re.match("(.*[\u4E00-\u9FA5]+.*)", content):
                    file_array.append("[" + str(line_count) + "]:\t\"" + content + "\"")
                    dic = {}
                    dic["path"] = path
                    dic["filename"] = filename
                    dic["msg"] = content
                    dic["content"] = add + content + add
                    dic["line_count"] = line_count
                    keys = path.split(lua_path)
                    key = keys[1]
                    if not (key in replace_dic):
                        replace_dic[key] = []
                    replace_dic[key].append(dic)
                    isHas = True
            else:
                # 记录文本内容
                content = content + c
        else:
            # 是否是横且之前也是
            if c == '-' and last_char == '-':
                # 不再判断后面
                return isHas
            elif c == '\'' or c == '\"' :  # 是否是引号
                # 标记
                quo_str = c
                content = ""
            
            
        last_char = c
        
    return isHas  
    

# 存储记录
def save():
    # 拼接字符串
    content = "\n".join(array)

    f = open(save_path, 'w', encoding='utf-8')
    f.write(content)
    f.close()

def load_cn_config():
    file = open(cn_path, "r",encoding='UTF-8')
    while True:
        line = file.readline()
        if not line:
            break
        load_cn_line(line,cn_dic)
    file.close()

# 读取cn表内容
def load_cn_line(line, dic):
    isHas = False

    quo_str = None # 开头的引号
    last_char = None
    
    content = ""
    
    key = ""
    value = ""

    for c in line:
        # 是否在引号中
        if quo_str != None:
            # 是否是相同引号且之前不是转义
            if c == quo_str and last_char != '\\':
                # 撤掉引号标记
                quo_str = None
                if value == "":
                    value = content
                else:
                    key = content
                    dic[key] = value
            else:
                # 记录文本内容
                content = content + c
        else:
            # 是否是横且之前也是
            if c == '-' and last_char == '-':
                # 不再判断后面
                return isHas
            elif c == '\'' or c == '\"' :  # 是否是引号
                # 标记
                quo_str = c
                content = ""
        last_char = c
        
    return isHas

def replace_info(item_list):
    if len(item_list) == 0:
        return
    path = item_list[0]["path"]
    file = open(path,"r",encoding="utf-8")
    lines = [""]
    while 1:
        line = file.readline()
        if not line:
            break
        lines.append(line)
    file.close()
    file = open(path,"w",encoding="utf-8")
    for item in item_list:
        line_count = item["line_count"]
        replace_str = get_replace_str(item["msg"])
        lines[line_count] = lines[line_count].replace(item["content"],replace_str,1)
        print("将 " + item["content"] + " 替换成 " + replace_str)
    print(path + " 替换完成\n")
    file.writelines(lines)
    file.close()

def get_replace_str(content):
    if content in cn_dic:
        return "public_func.GetWord('"+ cn_dic[content] +"')"
    elif content in target_dic:
        return "public_func.GetWord('"+ target_dic[content] +"')"
    else:
        auto_target.targetcount = auto_target.targetcount + 1 
        target_dic[content] = "auto_" + str(auto_target.targetcount)
        return "public_func.GetWord('"+ target_dic[content] +"')"


def filter_replace_item():
    for key in replace_dic:
        filename = key
        item_list = replace_dic[key]
        if not filename in ignore.ignore_list:
            if filename in white.white_list:
                replace_info(item_list)
            else:
                print("是否替换文件 " + filename + " ? \n")
                is_in = ""
                while True:
                    is_in = input()
                    if is_in in input_list:
                        break

                if is_in == "y":
                    print("替换 " + filename)
                    white.white_list.append(filename)
                    replace_info(item_list)
                elif is_in == "n":
                    print("忽略 " + filename + "\n")
                    ignore.ignore_list.append(filename)
                    continue
                elif is_in == "over":
                    break


def main():
    # 判断lua路径
    format_u3d_asset(lua_path, "")
    # 保存
    save()
    print("文件总数 ：" +str(file_count))
    load_cn_config()
    filter_replace_item()

    ignore_file = open("ignore.py","w",encoding="utf-8")
    msg = "ignore_list = [\n"
    for item in ignore.ignore_list:
        item = item.replace("\\","\\\\")
        msg = msg +"'"+ item +"',\n"
    msg = msg + "]"
    ignore_file.write(msg)
    ignore_file.close()

    white_file = open("white.py","w",encoding="utf-8")
    msg = "white_list = [\n"
    for item in white.white_list:
        item = item.replace("\\","\\\\")
        msg = msg +"'"+ item +"',\n"
    msg = msg + "]"
    white_file.write(msg)
    white_file.close()

    auto_file = open("auto_target.py","w",encoding="utf-8")
    msg = "targetcount = " + str(auto_target.targetcount)
    auto_file.write(msg)
    auto_file.close()

    replace_target = open("replace_target.lua","w",encoding="utf-8")
    msg = ""
    for key in target_dic:
        msg = msg +  'gs_all_string_cn["'+ target_dic[key] +'"] = "' + key +'"\n'
    replace_target.write(msg)
    replace_target.close()

    print("Finished...")

main()