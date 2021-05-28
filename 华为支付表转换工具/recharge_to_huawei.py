import xlrd
import xlwt
import os
import math

config_recharge_path = "D:\\Work\\svn\\"

def input_dir():
    file_name = ""
    while True:
        print(" 输入目录名字 ")
        dir_name = input()
        path = config_recharge_path + dir_name
        if os.path.isdir(path):
            file_name = path + "\\excel\\recharge.xls"
            if os.path.exists(file_name):
                break
            else:
                print(file_name + " 不存在 !")
        else:
            print(path + " 不是正确目录，请输入正确目录")
    return file_name

def read_recharge(fliename):
    workbook = xlrd.open_workbook(fliename)
    sheet_name = workbook.sheet_names()[0]
    sheet = workbook.sheet_by_name(sheet_name)
    nrows = sheet.nrows
    recharge_info = []
    count = 0
    for index in range(3,nrows):
        if count == 0:
            recharge_info.append([])
        add_list = recharge_info[-1]
        item = []
        proid = sheet.row_values(index)[0]
        item.append(proid)

        item.append(0)
        
        name = sheet.row_values(index)[4]
        desc = sheet.row_values(index)[6]
        desc = desc.replace("#","。")
        item.append("zh_TW|"+name+"|"+desc)

        price = sheet.row_values(index)[14]
        price_str = "US;" + str(price)+";TW;"+ str(format(29*price, '.2f'))+";HK;"+str(format(7.8*price, '.2f'))+";MO;"+ str(format(8*price, '.2f'))
        item.append(price_str)
        add_list.append(item)
        count = count + 1
        if count == 200:
            count = 0
    workbook.release_resources()
    return recharge_info

def write_excel(recharge_info):
    add = 0
    for add_list in recharge_info:
        add = add + 1
        workbook = xlwt.Workbook(encoding = 'utf-8')
        worksheet = workbook.add_sheet("Sheet1")
        worksheet.write(0, 0, 'ProductId')
        worksheet.write(0, 1, 'ProductType')
        worksheet.write(0, 2, 'Locale Title Description')
        worksheet.write(0, 3, 'Price')
        count = 1
        for item in add_list:
            count = count + 1
            for index in range(len(item)):
                worksheet.write(count, index, item[index])
        workbook.save('Product Batch Adding' + str(add)+'.xls')




def main():
    name = input_dir()
    recharge_info = read_recharge(name)
    write_excel(recharge_info)


main()
