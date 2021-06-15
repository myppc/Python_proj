import os
from db.db_item import db_item
import db.config as config
import re

db_instance = None

class db_loader:
    indexs = {}
    def get_ins():
        global db_instance
        if not db_instance:
            db_instance = db_loader()
        return db_instance

    def __init__(self):
        self.load_all_db()
    
    def load_all_db(self):
        file_list = os.listdir(config.db_data_path)
        for item in file_list:
            if re.search(".json",item):
                db_name = item.split(".")[0]
                self.load_db(db_name)

    def create_db(self,db_name):
        if self.check_db_exist(db_name):
            print("ERROR :create fail,db is exist!")
        else:
            self.indexs[db_name] = db_item(db_name)
            

    def check_db_exist(self,db_name):
        db_name = str(db_name)
        if db_name in self.indexs:
            return True
        else: 
            return False

    def get_db(self,db_name):
        db_name = str(db_name)
        if db_name in self.indexs:
            return self.indexs[db_name]
        else:
            return None

    def load_db(self,db_name):
        db_name = str(db_name)
        if not self.check_db_exist(db_name):
            self.create_db(db_name)
        return self.indexs[db_name]

    def close(self):
        print(self.indexs)
        for item in self.indexs:
            item.close()
