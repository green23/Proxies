# coding:utf-8
import pymongo
from __builtin__ import isinstance

from config import DB_CONFIG

'''
sql操作的基类
包括ip，端口，types类型(0高匿名，1透明)，protocol(0 http,1 https http),country(国家),area(省市),updatetime(更新时间)
 speed(连接速度)
'''


class MongoHelper(object):

    def __init__(self):
        self.host = DB_CONFIG['dbHost']
        self.port = DB_CONFIG['dbPort']
        self.db = pymongo.MongoClient(host=self.host, port=self.port)[DB_CONFIG['dbName']]
        self.collect = self.db[DB_CONFIG['dbCollect']]

    def insert(self, value):
        if isinstance(value, dict):
            self.collect.upsert(value)

    def batch_insert(self, values):
        if isinstance(values, list):
            data = [value for value in values if value is not None]
            self.collect.upsert(data)

    def delete(self, value):
        # self.collect.remove({'updatetime': {'$lt': date}})
        self.collect.remove(value)

    def batch_delete(self, values):
        pass

    def update(self, old, new):
        self.collect.update(old, new, upsert=True)

    def selectAll(self):
        return self.collect.find()

    def selectOne(self, value):
        return self.collect.find_one(value)

    def selectCount(self):
        return self.collect.count()

    def close(self):
        pass


class SqlHelper(object):
    def __init__(self):
        pass

    def insert(self, value):
        pass

    def batch_insert(self, values):
        pass

    def delete(self, condition):
        pass

    def batch_delete(self, values):
        pass

    def update(self, condition, value):
        pass

    def select(self, condition):
        pass

    def selectOne(self, tableName, condition, value):
        pass

    def close(self):
        pass