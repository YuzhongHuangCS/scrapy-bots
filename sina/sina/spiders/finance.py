# -*- coding: utf-8 -*-
from scrapy.http import Request
from scrapy.http import HtmlResponse
from scrapy.spider import Spider
from pyquery import PyQuery as pyq

class FinanceSpider(Spider):
	name = 'finance'

	def __init__(self, category=None, *args, **kwargs):
		super(FinanceSpider, self).__init__(*args, **kwargs)
		self.allowed_domains = ['sina.com.cn']

	def start_requests(self):
		# for days don't have content, sina will return 404 and will ignore by scrapy
		for year in range(2007, 2007+1):
			for month in range(1, 12+1):
				for day in range(1, 31+1):
					url = "http://news.sina.com.cn/old1000/news1000_%s%s%s.shtml" % (year, str(month).rjust(2, '0'), str(day).rjust(2, '0'))
					yield Request(url, callback=self.parse2000List)

	'''
	def parse(self, response):
		for url in response.css('a::attr(href)').extract():
			if 'archives' in url:
				if 'category' in url:
					yield Request(url)
				else:
					if 'author' not in url:
						yield Request(url, callback=self.parseTwo)
	'''

	def parse2000List(self, response):
		response = response.replace(body=response.body.decode('gb2312', 'ignore').encode('utf-8'), encoding='utf-8')
		for row in response.css('li'):
			if row.css('::text').extract()[0].encode('utf-8') == "[财经] ":
				url = row.css('a::attr(href)').extract()[0]
				yield Request(url, callback=self.parse2000Post)

	def parse2000Post(self, response):
		response = response.replace(body=response.body.decode('gb2312', 'ignore').encode('utf-8'), encoding='utf-8')
		rawTitle = response.css('title::text').extract()[0]
		d = pyq(response.css('div#artibody').extract()[0])
		print d.text()

		'''
		data = {
			url: response.url
			title: rawTitle[:rawTitle.find('_')]
			body: 
		}
		'''

