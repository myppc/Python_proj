
import os 
import shutil
import picture_same_check as same_checker
import config

dest_path = config.dest_path
src_path = config.src_path
un_copy_path = config.un_copy_path

dest_dic = {}
src_dic = {}
repeat_dest_dic = {}
repeat_src_file = {}
un_copy_dic = {}
warn_dic = {}
#检查字符串中是否有中文
def cat_chinese(s):
	for c in s:
		if ('\u4e00' <= c <= '\u9fa5'):
			return True
	return False

#搜索指定目录下的图片路径
def serch_pic_file(dir_str,dic,repeat_dic):
    for lists in os.listdir(dir_str): 
        path = os.path.join(dir_str, lists) 
        if os.path.isdir(path): 
            serch_pic_file(path,dic,repeat_dic)
        else:
        	point_pos = path.find(".",1)
        	if point_pos != -1 :
        		add = path[point_pos+1:]
        		if add=="png" or add=="jpg":
        			file_name = lists
        			point_pos2 = file_name.find(".",1)
        			key = file_name[:point_pos2]
        			if cat_chinese(key):
        				continue
	        		if key in dic:
	        			record_repeat_pic(key,dic[key],repeat_dic)
	        			record_repeat_pic(key,path,repeat_dic)
	        			del dic[key]
	        			continue
        			dic[key] = path
        			


def record_repeat_pic(file_name,path,repeat_dic): 
	if not (file_name in repeat_dic):
		repeat_dic[file_name] = []
	repeat_dic[file_name].append(path)

#从资源目录拷贝图片到指定目录，如果资源目录中有没有用到的图片，则将图片复制到un_copy_path下，等待肉眼替换，并且记录文件路径
def copy_files():
	count = 0
	for src_key in src_dic:
		if src_key in dest_dic:
			spath = src_dic[src_key]
			dpath = dest_dic[src_key]
			shutil.copyfile(spath,dpath)
			count = count + 1
		else:
			spath = src_dic[src_key]
			point_pos = spath.find(".",1)
			add = spath[point_pos:]
			shutil.copyfile(spath,un_copy_path+src_key+add)
			un_copy_dic[src_key] = src_dic[src_key]
	print("copy succ,copy file num " + str(count))

#如果要替换的文件在工程中有多张，则挨个对比，如果工程里面重复的图片每张都相似，则将工程中所有图片一起替换，不然就放弃该图片
def copy_repeat_files():
	for src_key in src_dic:
		if src_key in repeat_dest_dic:
			repeat_list = repeat_dest_dic[src_key]
			spath = src_dic[src_key]
			first = repeat_list[0]
			is_replace = True
			for repeat_item in repeat_list:
				if not same_checker.check(first,repeat_item):
					is_replace = False
					break
			if is_replace:
				for repeat_item in repeat_list:
					shutil.copyfile(spath,repeat_item)
				del repeat_dest_dic[src_key]
			else:
				un_copy_dic[src_key] = src_dic[src_key]
				warn_dic[src_key] = repeat_list


#记录没有使用的图片
def save_un_copy_file():
	f = open("未使用的图片.txt","w+",encoding = "UTF-8")
	msg = ""
	for key in un_copy_dic:
		msg = msg + key +" " + un_copy_dic[key] +"\n"
	f.write(msg)
	f.close()

#将重复图片的路径写入文件记录
def save_repeat_file_path(repeat_dic,file_name):
	f = open(file_name+".txt","w+",encoding = "UTF-8")
	msg = ""
	for key in repeat_dic:
		msg = msg + key +":\n"
		path_list = repeat_dic[key]
		for path in path_list:
			msg = msg + path + "\n"
		msg = msg + "\n"	
	f.write(msg)
	f.close()

def main():
	if not os.path.isdir(dest_path): 
		print("dest_path error ! copy fail ")
		return
	if not os.path.isdir(src_path): 
		print("src_path error ! copy fail ")
		return
	serch_pic_file(dest_path,dest_dic,repeat_dest_dic)
	serch_pic_file(src_path,src_dic,repeat_src_file)
	copy_repeat_files()
	copy_files()
	save_un_copy_file()
	save_repeat_file_path(repeat_dest_dic,"目标目录重复")
	save_repeat_file_path(repeat_src_file,"资源目录重复")
	save_repeat_file_path(warn_dic,"机器识别的非相似图片")

main()
