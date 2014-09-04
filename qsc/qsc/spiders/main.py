# -*- coding: utf-8 -*-
from scrapy.http import Request
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from pyquery import PyQuery as pyq
from pymongo import MongoClient
import gridfs

class MainSpider(CrawlSpider):
	name = "main"
	allowed_domains = ['www.qsc.zju.edu.cn']
	start_urls = ['http://www.qsc.zju.edu.cn/index.php/category/new/']

	rules = (
		Rule(LinkExtractor(allow=('/category/'), deny=('/apps/'))),
		Rule(LinkExtractor(allow=('/post/')), callback='parsePost'),
	)

	def __init__(self):
		super(MainSpider, self).__init__()
		self.db = MongoClient().qsc
		self.collection = self.db.post
		self.fs = gridfs.GridFS(self.db)
		self.fsCollection = self.db.fs.files

	def parsePost(self, response):

		def filterRule(url):
			if '/attachment/' in url:
				return url 

		d = pyq(response.body)
		post = {
			"url": response.url,
			"title": response.css('#passage-title::text').extract()[0],
			"category": response.css('div.list-title-word::text').extract()[0],
			"datetime": response.css('#passage-info::text').extract()[0].split(' | ')[0],
			"hit": response.css('#passage-info::text').extract()[0].split(' | ')[1],
			"detail":  d('#passage-detail').text(),
			"img": filter(filterRule, response.css('img::attr(src)').extract()),
		}

		self.collection.update({"url": post['url']}, post, True)

		'''
		the scheduler of yield here is different from that in tornado or twisted,
		it will call `next()` immediately, rather than the IO has completed
		so just use yield, it is still in parallel 
		'''
		for url in post['img']:
			yield Request(url, callback=self.saveImage)

	def saveImage(self, response):
		id = self.fs.put(response.body)
		mime = response.headers['Content-Type']
		self.fsCollection.update({"_id": id}, {'$set': {"url": response.url, "Content-Type": mime}}, True)