from typing import Iterable
from pymongo import MongoClient


conn_str = "mongodb://localhost:27017/"


def test_connection(ip_address=conn_str):
        maxSevSelDelay = 1
        try:
            client = MongoClient(ip_address, serverSelectionTimeoutMS=maxSevSelDelay)
            client.close()
            return True
        except Exception as e:
            print(str(e))
            return False


class DB:

    def __init__(self, database="pg-psa", collection="inspections"):  # 'mongodb://localhost:27017/'):
        super(DB, self).__init__()
        self.client = MongoClient(conn_str)
        self.database = self.client[database]
        self.collection = self.database[collection]
    
    def select_colection(self, col: str):
        self.collection = self.database[col]

    def sort(self, keyword):
        return self.collection.find().sort(keyword, -1)

    def delete_one(self, query):
        return self.collection.delete_one(query)

    def delete_many(self, query):
        return self.delete_many(query)

    def delete_all(self):
        return self.collection.delete_many({})

    def insert_one(self, document):
        return self.collection.insert_one(document)
    
    def insert_many(self, docs: Iterable):
        return self.collection.insert_many(docs)

    def find(self, query):
        return self.collection.find(query)  # { keyword : value })

    def find_all(self, keyword=None):
        return self.collection.find()

    def delete_collection(self):
        return self.collection.drop()

    def create_collection(self, name):
        return self.database.create_collection(name=name)

    def update_connection(self, ip, db, col):
        self.client.close()
        self.client = MongoClient(ip, serverSelectionTimeoutMS=2)
        self.database = self.client[db]
        self.collection = self.database[col]
        print(self.client.server_info())


if __name__ == "__main__":
    db = DB()

    ic(test_connection())