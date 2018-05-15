from pymongo import MongoClient

class db_client():
    def __init__(self,db_str):
        client = MongoClient('mongodb://localhost:27017/')
        self.db = client[db_str]

    def get_joint_name(self,str_1,str_2):
        return '_'.join([str_1,str_2])
        
    def get_collection(self,collection_name):
        #return getattr(self.db,collection_name)
        return self.db[collection_name]

    def get_collection_names(self):
        return self.db.collection_names()

    def get_msi_name(self):
        return '_Trend_Vizor_msiexe'


'''     
def get_db_client():
    client = MongoClient('mongodb://localhost:27017/')
    db = client["log_parser_ai"]
    return db
'''

if __name__ == '__main__':
    client = db_client('log_parser_ai')
    c = client.get_collection('test_table2')
    c.insert_one({'k12':'v12','k23':'v23'})

    #db = get_db_client()
    #c = db.test_table
    #c.insert({'k1':'v1','k2':'v2'})
