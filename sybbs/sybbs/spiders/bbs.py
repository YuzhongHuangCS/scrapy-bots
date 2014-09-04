# -*- coding: utf-8 -*-
from scrapy.http import Request
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from pyquery import PyQuery as pyq
from pymongo import MongoClient

class MainSpider(CrawlSpider):
	name = "bbs"
	allowed_domains = ['0575bbs.com']
	start_urls = [
		'http://www.0575bbs.com/',
		'http://bbs.0575bbs.com/',
		'http://food.0575bbs.com/',
		'http://travel.0575bbs.com/',
		'http://marry.0575bbs.com/',
		'http://baby.0575bbs.com/',
		'http://prepaid.0575bbs.com/',
	]

	rules = (
		Rule(LinkExtractor(allow=('thread-htm-fid', 'thread\.php\?fid')), callback='parseField', follow=True),
		Rule(LinkExtractor(allow=('read-htm-tid', 'read\.php\?tid')), callback='parseThread'),
	)

	def __init__(self):
		super(MainSpider, self).__init__()
		self.db = MongoClient().sybbs
		self.collection = self.db.thread

	def parseField(self, response):

		'''
		Exceptions:
		* stick top thread don't have field
		* global stick top even don't have timestamp
		* nested tags, use pyquery
		* based whether on '-' in time to test if it is a recent thread
		'''

		for thread in response.css('tr.tr3'):
			try:
				if '-' in thread.css('td.author > p > a::text').extract()[0]:
					continue
			except Exception, e:
				continue

			author = thread.css('td.author > p > a')
			info ={
				"url": self.start_urls[0] + author.css('::attr(href)').extract()[0].replace('-page-e', '').replace('#a', ''),
				"timestamp": author.css('::attr(title)').extract()[0],
			}

			try:
				info['title'] = pyq(thread.css('a.subject_t').extract()[0]).text()
				info['field'] = thread.css('a.view::text').extract()[0].strip('[]')
			except Exception, e:
				pass

			self.collection.update({"url": info['url']}, {"$set": info}, True)

			'''
			the scheduler of yield here is different from that in tornado or twisted,
			it will call `next()` immediately, rather than the IO has completed
			so just use yield, it is still in parallel 
			'''
			yield Request(info['url'], callback=self.parseThread)


	def parseThread(self, response):
		url = response.url.replace('http://bbs', 'http://www')
		reply = []
		for floor in response.css('div.tpc_content').extract():
			reply.append(pyq(floor).text())

		self.collection.update({"url": response.url}, {'$set': {"reply": reply}}, True)