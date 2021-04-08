#检验是否含有中文字符
import time
import os 

root_dir = "./dir"

def cat_chinese(s):
	if len(s) > 300:
		return False
	for c in s:
		if ('\u4e00' <= c <= '\u9fa5'):
			return True
	return False

def read_file(file_name):
	fo = open(file_name, "r",encoding='UTF-8')
	text = fo.read()
	fo.close()
	return text


def cat_str(msg,file_name):
	msg2 = msg
	ret = []
	while True:
		start_pos = msg.find('"')
		if start_pos == -1:
			break
		end_pos = msg.find('"',start_pos + 1)
		if end_pos == -1 :
			print("ERROR FILE : " + file_name)
			return []
		item = msg[start_pos+1:end_pos]
		ret.append(item)
		msg = msg[end_pos+1:]

	while True:
		start_pos = msg2.find("'")
		if start_pos == -1:
			break
		end_pos = msg2.find("'",start_pos + 1)
		if end_pos == -1 :
			print("ERROR FILE : " + file_name)
			return []
		item = msg2[start_pos+1:end_pos]
		ret.append(item)
		msg2 = msg2[end_pos+1:]
	return ret

def filter_cn(item_list):
	ret = []
	for item in item_list:
		if cat_chinese(item):
			ret.append(item)
	return ret

def filter_dirs(dir_str):
    for lists in os.listdir(dir_str): 
        path = os.path.join(dir_str, lists) 
        if os.path.isdir(path): 
            filter_dirs(path)
        else:
        	point_pos = path.find(".",1)
        	if point_pos != -1 :
        		add = path[point_pos+1:]
        		if add=="lua":
        			text = read_file(path)
        			item_list = cat_str(text,path)
        			cn_list = filter_cn(item_list)
        			print(cn_list)

def main():
	# text = read_file("monster_atk_str.lua")
	# item_list = cat_str(text)
	# cn_list = filter_cn(item_list)
	# print(cn_list)
	filter_dirs(root_dir)

main()
