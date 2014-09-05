# -*- coding: utf-8 -*-
from scrapy.http import Request
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from pyquery import PyQuery as pyq
from pymongo import MongoClient

class MainSpider(CrawlSpider):
	name = "bbs"
	allowed_domains = ['dsybbs.com']
	start_urls = [
		'http://www.dsybbs.com/',
	]

	'''
	Forbid directly fetch thread pages, or follow field pages
	Because haven't check if they are recent post, and by always, not.
	Manually check and schedule later.
	'''
	rules = (
		Rule(LinkExtractor(allow=('/forum.*\.html')), callback='parseField'),
	)

	def __init__(self):
		super(MainSpider, self).__init__()
		self.db = MongoClient().dsybbs
		self.collection = self.db.thread

	def parseField(self, response):

		'''
		Check if need to fetch next field page
		Exceptions:
		* Login required pages.
		'''
		try:
			if '-' not in response.css('div#threadlist > div.bm_c table tbody:last-child td.by:last-child > em > a > span::text').extract()[0]:
				nextPageUrl = self.start_urls[0] + response.css('span#fd_page_bottom > div.pg > strong + a::attr(href)').extract()[0].replace(self.start_urls[0], '')
				yield Request(nextPageUrl, callback=self.parseField)
		except Exception, e:
			# This exception is caused by non-recent threads didn't have <span> within <a>
			# Every un-matched thread will raise this exception, have to comment out
			# self.log('Exception occured: %s, %s' % (response.url, e))
			pass

		'''
		Filter and fetch thread page
		Based whether on '-' in time to test if it is a recent thread
		For nested tags, use pyquery
		Exceptions:
		* stick top thread don't have field
		* global stick top even don't have timestamp
		'''

		for thread in response.css('div#threadlist > div.bm_c table tr'):
			try:
				if '-' in thread.css('td.by:last-child > em > a > span::text').extract()[0]:
					continue
			except Exception, e:
				# This exception is caused by non-recent threads didn't have <span> within <a>
				# Every un-matched thread will raise this exception, have to comment out
				# self.log('Exception occured: %s, %s' % (response.url, e))
				continue

			info ={}
			try:
				info['url'] = thread.css('th > a::attr(href)').extract()[0]
				info['timestamp'] = thread.css('td.by:last-child > em > a > span::attr(title)').extract()[0]
				info['title'] = thread.css('th > a::text').extract()[0]
				info['field'] = thread.css('th > em > a::text').extract()[0]
			except Exception, e:
				# This exception is caused by stick top thread didn't have field
				# It also occured very frequently, have to comment out
				# self.log('Exception occured: %s, %s' % (response.url, e))
				pass

			self.collection.update({"url": info['url']}, {"$set": info}, True)

			'''
			the scheduler of yield here is different from that in tornado or twisted,
			it will call `next()` immediately, rather than the IO has completed
			so just use yield, it is still in parallel 
			'''
			yield Request(info['url'], callback=self.parseThread)


	def parseThread(self, response):
		reply = []
		for floor in response.css('div#postlist > div > table > tr:first-child > td.plc > div.pct').extract():
			reply.append(pyq(floor).text())

		self.collection.update({"url": response.url}, {'$set': {"reply": reply}}, True)
