# -*- coding: utf-8 -*-
from scrapy.http import Request
from scrapy.spider import Spider
from pyquery import PyQuery as pyq
from pymongo import MongoClient
from datetime import date, timedelta

class FinanceSpider(Spider):
	name = 'finance'

	'''
	intervals:
		[1999.05.26, 1999.07.25) -> need right justify
		[1999.07.25, 2001.02.01) -> needn't 
		[2001.02.01, 2007.01.20) -> need right justify

	'''
	def __init__(self, category=None, *args, **kwargs):
		super(FinanceSpider, self).__init__(*args, **kwargs)
		self.allowed_domains = ['sina.com.cn']
		self.start_urls = []
		self.db = MongoClient().sina
		self.collection = self.db.finance

	def start_requests(self):

		today = date(1999, 5, 26)
		step = timedelta(1)

		while True:
			url = "http://news.sina.com.cn/old1000/news1000_%s%s%s.shtml" % (today.year, str(today.month).rjust(2, '0'), str(today.day).rjust(2, '0'))
			yield Request(url, callback=self.parse2000List)
			today += step
			if today.year == 1999 and today.month == 7 and today.day == 25:
				break

		while True:
			url = "http://news.sina.com.cn/old1000/news1000_%s%s%s.shtml" % (today.year, today.month, today.day)
			yield Request(url, callback=self.parse2000List)
			today += step
			if today.year == 2001 and today.month == 2 and today.day == 1:
				break

		while True:
			url = "http://news.sina.com.cn/old1000/news1000_%s%s%s.shtml" % (today.year, str(today.month).rjust(2, '0'), str(today.day).rjust(2, '0'))
			yield Request(url, callback=self.parse2000List)
			today += step
			if today.year == 2007 and today.month == 1 and today.day == 20:
				break

	def parse2000List(self, response):
		response = response.replace(body=response.body.decode('gb2312', 'ignore').encode('utf-8'), encoding='utf-8')
		for row in response.css('li'):
			if row.css('::text').extract()[0].encode('utf-8') == "[财经] ":
				url = row.css('a::attr(href)').extract()[0]
				yield Request(url, callback=self.parse2000Post, priority=10)

	def parse2000Post(self, response):
		def analysys(response):
			try:
				d = pyq(response.css('div#artibody').extract()[0])
				data = {
					"url": response.url,
					"title": response.css('h1#artibodyTitle::text').extract()[0],
					"body": d.text(),
					"date": response.css('span#pub_date::text').extract()[0],
				}
				return data

			except Exception, e:
				print e

			try:
				d = pyq(response.css('td[valign="top"]').extract()[2])
				data = {
					"url": response.url,
					"title": response.css('font[size="5"]::text').extract()[0],
					"body": d.text(),
					"date": response.css('font[face="Arial"]').extract()[0],
				}
				return data

			except Exception, e:
				print e

			raise NotImplementedError('No matched analysys method')

		data = analysys(response.replace(body=response.body.decode('gb2312', 'ignore').encode('utf-8'), encoding='utf-8'))
		self.collection.update({"url": data['url']}, {"$set": data}, True)