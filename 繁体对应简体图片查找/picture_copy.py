
import os
import shutil
import config



jianti_src_path = config.jianti_src_path
fanti_path = config.fanti_path
jianti_output_path = config.jianti_output_path

dest_list = []
un_exists_file = []

def filter_pic(dir_str,dest_list ):
	for lists in os.listdir(dir_str):
		path = os.path.join(dir_str, lists)
		if os.path.isdir(path):
			filter_pic(path,dest_list)
		else:
			point_pos = path.find(".",1)
			if point_pos != -1 :
				add = path[point_pos+1:]
				if add=="png" or add=="jpg":
					file_name = lists
					record_path = path.split(fanti_path)[1]
					dest_list.append(record_path)
					print( record_path)


def copy_jianti_to_dest():
	for path in dest_list:
		jianti_file_path = jianti_src_path + path
		if os.path.exists(jianti_file_path):
			if not os.path.exists(jianti_output_path + path):
				create_dir(path)
				shutil.copyfile(jianti_file_path,jianti_output_path + path)
		else:
			un_exists_file.append(fanti_path + path)

def create_dir(path):
	split_list = path.split("\\")
	cur_path = jianti_output_path
	for num in range(1,len(split_list)):
		if split_list[num].find(".") != -1:
			continue
		else:
			cur_path = cur_path + "\\" + split_list[num]
			if not os.path.exists(cur_path):
				os.mkdir(cur_path)

def save_un_exists_path(unexists_list,file_name):
	f = open(file_name+".txt","w+",encoding = "UTF-8")
	msg = ""
	for info in unexists_list:
		msg = msg + info +"\n"
	f.write(msg)
	f.close()

def main():
	filter_pic(fanti_path,dest_list)
	copy_jianti_to_dest()
	save_un_exists_path(un_exists_file,"缺省图片")

main()
