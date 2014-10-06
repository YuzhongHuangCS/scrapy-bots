# -*- coding: utf-8 -*-
from scrapy.http import Request
from scrapy.spider import Spider
from pyquery import PyQuery as pyq
from pymongo import MongoClient
from datetime import date, timedelta
import json

class FinanceSpider(Spider):
	name = 'finance'

	'''
	intervals:
		[1999.05.26, 1999.07.25) -> need right justify
		[1999.07.25, 2001.02.01) -> needn't 
		[2001.02.01, 2007.01.20) -> need right justify
		[2007.01.20, 2007.12.12) -> js, sort by time
		[2007.12.12, 2014.10.05) -> js, by category
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
			yield Request(url, callback=self.parseList)
			today += step
			if today.year == 1999 and today.month == 7 and today.day == 25:
				break

		while True:
			url = "http://news.sina.com.cn/old1000/news1000_%s%s%s.shtml" % (today.year, today.month, today.day)
			yield Request(url, callback=self.parseList)
			today += step
			if today.year == 2001 and today.month == 2 and today.day == 1:
				break

		while True:
			url = "http://news.sina.com.cn/old1000/news1000_%s%s%s.shtml" % (today.year, str(today.month).rjust(2, '0'), str(today.day).rjust(2, '0'))
			yield Request(url, callback=self.parseList)
			today += step
			if today.year == 2007 and today.month == 1 and today.day == 20:
				break

		while True:
			url = "http://news.sina.com.cn/old1000/news1000_%s%s%s/data0.js" % (today.year, str(today.month).rjust(2, '0'), str(today.day).rjust(2, '0'))
			yield Request(url, callback=self.parseJson)
			today += step
			if today.year == 2007 and today.month == 12 and today.day == 12:
				break

		while True:
			url = "http://rss.sina.com.cn/rollnews/finance/%s%s%s.js" % (today.year, str(today.month).rjust(2, '0'), str(today.day).rjust(2, '0'))
			yield Request(url, callback=self.parseJsObject)
			today += step
			if today.year == 2008 and today.month == 12 and today.day == 12:
				break

	def parseList(self, response):
		response = response.replace(body=response.body.decode('gb2312', 'ignore').encode('utf-8'), encoding='utf-8')
		for row in response.css('li'):
			if "财经" in row.css('::text').extract()[0].encode('utf-8'):
				url = row.css('a::attr(href)').extract()[0]
				if '..' in url:
					url = 'http://news.sina.com.cn' + url[2::]
				else:
					if 'sina.com.cn' not in url:
						url = 'http://news.sina.com.cn' + url

				yield Request(url, callback=self.parsePost, priority=10)

	def parseJson(self, response):
		url = bytearray(response.url)
		i = url[-4] + 1
		url[-4] = i
		yield Request(str(url), callback=self.parseJson)

		response = response.replace(body=response.body.decode('gb2312', 'ignore').encode('utf-8'), encoding='utf-8')
		body = response.body
		start = body.index('[[')
		end = body.index(']]') + 2
		data = json.loads(body[start:end].replace('\\', ''), strict=False)
		for item in data:
			yield Request(item[3], callback=self.parsePost, priority=10)

	def parseJsObject(self, response):
		def dig(body):
			lIndex = body.index('link') + 6
			try:
				while True:
					lIndex = body.index('link', lIndex) + 6
					rIndex = body.index('"', lIndex)
					yield body[lIndex:rIndex]
			except ValueError, e:
				return

		response = response.replace(body=response.body.decode('gb2312', 'ignore').encode('utf-8'), encoding='utf-8')
		for url in dig(response.body):
			yield Request(url, callback=self.parsePost, priority=10)

	def parsePost(self, response):
		def analysys(response):
			try:
				d = pyq(response.css('div#artibody').extract()[0])
				data = {
					"url": response.url,
					"title": response.css('h1#artibodyTitle::text').extract()[0],
					"body": d.text(),
					"date": response.css('span#pub_date::text').extract()[0],
					"parsed": "1"
				}
				return data

			except IndexError, e:
				pass

			try:
				d = pyq(response.css('td[valign="top"]').extract()[2])
				data = {
					"url": response.url,
					"title": response.css('font[size="5"]::text').extract()[0],
					"body": d.text(),
					"date": response.css('font[face="Arial"]').extract()[0],
					"parsed": "2"
				}
				return data

			except IndexError, e:
				pass

			try:
				d = pyq(response.css('td[valign="top"]').extract()[2])
				data = {
					"url": response.url,
					"title": d('h3').text(),
					"body": d.text(),
					"date": d('font[face="Arial"]').text(),
					"parsed": "3"
				}
				return data

			except IndexError, e:
				pass

			try:
				d = pyq(response.css('td[valign="top"]').extract()[1])
				data = {
					"url": response.url,
					"title": d('font[size="5"]').text(),
					"body": d.text(),
					"date": d('font[face="Arial"]').text(),
					"parsed": "4"
				}
				return data

			except IndexError, e:
				pass

			try:
				d = pyq(response.css('body').extract()[0])
				data = {
					"url": response.url,
					"title": d('div#artibodyTitle').text(),
					"body": d('div#artibody').text(),
					"date": d('div.from_info').text(),
					"parsed": "5"
				}
				return data

			except IndexError, e:
				pass

			raise NotImplementedError('No matched analysys method')

		data = analysys(response.replace(body=response.body.decode('gb2312', 'ignore').encode('utf-8'), encoding='utf-8'))
		self.collection.update({"url": data['url']}, {"$set": data}, True)
