# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from pymongo import MongoClient

class StoreToMongoDB(object):
    def __init__(self):
        super(StoreToMongoDB, self).__init__()
        self.client = MongoClient()
        self.collection = self.client.deepin.blog

    def process_item(self, item, spider):
    	post = {
    		"url": item['url'][0],
			"title": item['title'][0],
			"date": item['date'][0],
			"author": item['author'][0],
			"content": item['content'][0],
    	}
        self.collection.update({"url": post['url']}, post, True)