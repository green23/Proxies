# coding:utf-8
import datetime
from gevent.pool import Pool
import requests
import time
from config import TEST_URL
import config
from db.SQLiteHelper import SqliteHelper
from db.SqlHelper import MongoHelper
from gevent import monkey

monkey.patch_all()


class Validator(object):
    def __init__(self, sqlHelper):
        self.detect_pool = Pool(config.THREADNUM)
        self.detect_pool = Pool(config.THREADNUM)
        self.sqlHelper = sqlHelper

    def run_db(self):
        '''
        从数据库中检测
        :return:
        '''
        try:
            # 首先将超时的全部删除
            self.deleteOld()
            # 接着检测剩余的ip,是否可用
            results = self.sqlHelper.selectAll()
            self.detect_pool.map(self.detect_db, results)


            return self.sqlHelper.selectCount()  # 返回最终的数量
        except Exception, e:
            print e
            return 0

    def run_list(self, results):
        '''
        这个是先不进入数据库，直接从集合中删除
        :param results:
        :return:
        '''
        # proxys=[]
        # for result in results:
        proxys = self.detect_pool.map(self.detect_list, results)
        # 这个时候proxys的格式是[{},{},{},{},{}]
        return proxys

    def deleteOld(self):
        '''
        删除旧的数据
        :return:
        '''
        condition = datetime.datetime.now() - datetime.timedelta(minutes=config.MAXTIME)
        value = {'createtime': {'$lt': condition}}
        self.sqlHelper.delete(value)

    def detect_db(self, result):
        '''

        :param result: 从数据库中检测
        :return:
        '''
        ip = str(result['ip'])
        port = str(result['port'])
        proxies = {"http": "http://%s:%s" % (ip, port)}
        start = time.time()
        try:
            r = requests.get(url=TEST_URL, headers=config.HEADER, timeout=config.TIMEOUT, proxies=proxies)

            if not r.ok:
                self.sqlHelper.delete({'ip': ip, 'port': int(port)})
                print 'delete %s:%s' % (ip, port)
            else:
                speed = round(time.time() - start, 2)
                self.sqlHelper.update(result, {"$set": {'speed': speed, 'updatetime': datetime.datetime.now()}})
                print 'success ip = %s,speed = %s' % (ip, speed)
        except Exception, e:
            self.sqlHelper.delete({'ip': ip, 'port': int(port)})

    def detect_list(self, proxy):
        '''
        :param proxy: ip字典
        :return:
        '''

        ip = proxy['ip']
        port = proxy['port']
        proxies = {"http": "http://%s:%s" % (ip, port)}
        start = time.time()
        try:
            r = requests.get(url=TEST_URL, headers=config.HEADER, timeout=config.TIMEOUT, proxies=proxies)

            if not r.ok:
                proxy = None

            else:
                speed = round(time.time() - start, 2)
                print 'success ip = %s, speed = %s' % (ip, speed)
                proxy['speed'] = speed
        except Exception, e:
            proxy = None
        return proxy


if __name__ == '__main__':
    # v = Validator()
    # results=[{'ip':'192.168.1.1','port':80}]*10
    # results = v.run(results)
    # print results
    pass
