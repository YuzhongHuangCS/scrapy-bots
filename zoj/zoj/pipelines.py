# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from pymongo import MongoClient
import scrapy.signals
from scrapy.signalmanager import SignalManager

class StoreToMongoDB(object):
    def __init__(self):
        super(StoreToMongoDB, self).__init__()
        self.client = MongoClient()
        self.collection = self.client.acm.problem
        manager = SignalManager()
        manager.connect(self.initialize, scrapy.signals.spider_opened)
        manager.connect(self.finalize, scrapy.signals.spider_idle)
 

    def process_item(self, item, spider):
        data = {
            "id": item['id'],
            "title": item['title'],
            "body": item['body']
        }
        self.collection.insert(data)
    
    def initialize():
        for i in range(100):
            print('initialize\n')
    
    def finalize():
        print('finalize')