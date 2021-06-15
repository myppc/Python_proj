import os
import db.config as config
import json
import copy

class db_item:
    name = ""
    data = {}
    is_flush = False
    def __init__(self,db_name):
        self.name = db_name
        path = config.db_data_path + db_name + ".json"
        if os.path.exists(path):
            file = open(path,"r+")
            self.data = json.load(file)
        else:
            file = open(path,"w+")
            file.write('{}') 
            file.close()

    def flush(self):
        path = config.db_data_path + self.name + ".json"
        jsonstr = json.dumps(self.data)
        file = open(path,"w+",encoding = "UTF-8")
        file.write(jsonstr)
        file.close()
        self.is_flush = False
    
    def set_info(self,key,value):
        self.data[key] = value
        self.is_flush = True

    def del_info(self,key):
        del self.data[key]
        self.is_flush = True
    
    def get_info(self,key):
        if key in self.data:
            ret = self.data[key]
            vtype = type(ret)
            if vtype == 'dict' or vtype == 'list':
                return copy.deepcopy(ret)
            else:
                return ret
        else:
            return None

    def get_all_keys(self):
        ret = list(self.data.items())
        return ret

    def get_all_info(self):
        return copy.deepcopy(self.data)

    def close(self):
        if self.is_flush:
            self.flush()



