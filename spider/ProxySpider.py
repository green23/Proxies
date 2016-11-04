# coding:utf-8
from gevent.pool import Pool
import requests
import time
import datetime
import config
from config import THREADNUM, parserList, MINNUM, UPDATE_TIME
from db.SQLiteHelper import SqliteHelper
from db.SqlHelper import MongoHelper
from spider.HtmlDownLoader import Html_Downloader
from spider.HtmlPraser import Html_Parser
from validator.Validator import Validator
from gevent import monkey

monkey.patch_all()

'''
这个类的作用是描述爬虫的逻辑
'''


class ProxySpider(object):
    def __init__(self):

        self.crawl_pool = Pool(THREADNUM)
        # self.sqlHelper = sqlHelper

    def run(self):
        # dbtype = {'Mongo': MongoHelper, 'Sqlite': SqliteHelper}
        while True:
            print 'spider beginning -------'
            # sqlHelper = SqliteHelper()
            sqlHelper = MongoHelper()
            print 'validator beginning -------'
            validator = Validator(sqlHelper)
            count = validator.run_db()
            # count = sqlHelper.selectCount()
            print 'validator end ----count=%s' % count
            if count < MINNUM:
                proxys = self.crawl_pool.map(self.crawl, parserList)
                # 这个时候proxys的格式是[[{},{},{}],[{},{},{}]]
                proxys_tmp = []
                for proxy in proxys:
                    proxys_tmp.extend(proxy)

                proxys = proxys_tmp
                print 'first_proxys--%s', len(proxys)
                # 这个时候proxys的格式是[{},{},{},{},{},{}]
                # 这个时候开始去重:
                proxys = [dict(t) for t in set([tuple(proxy.items()) for proxy in proxys])]

                print 'spider proxys -------%s' % type(proxys)
                proxys = validator.run_list(proxys)  # 这个是检测后的ip地址
                proxys = [value for value in proxys if value is not None]
                print 'end_proxys--%s', len(proxys)
                for proxy in proxys:
                    exist = sqlHelper.selectOne({'ip': proxy['ip'], 'port': proxy['port'], 'type': proxy['type']})
                    if exist:
                        sqlHelper.update(exist, {'$set': {'updatetime': datetime.datetime.now()}})
                    else:

                        sqlHelper.update({'ip': proxy['ip'], 'port': proxy['port']}, proxy)
                print 'success ip = %s' % sqlHelper.selectCount()
            print 'spider end -------'
            time.sleep(UPDATE_TIME)

    def crawl(self, parser):
        proxys = []
        html_parser = Html_Parser()
        for url in parser['urls']:
            response = Html_Downloader.download(url)
            if response != None:
                proxylist = html_parser.parse(response, parser)
                if proxylist != None:
                    proxys.extend(proxylist)
        return proxys


if __name__ == "__main__":
    spider = ProxySpider()
    spider.run()
