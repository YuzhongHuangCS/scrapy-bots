# -*- coding: utf-8 -*-
from scrapy.http import Request
from scrapy.contrib.spiders import XMLFeedSpider
from bbsRss.sites import Sites
from pyquery import PyQuery as pyq
from pymongo import MongoClient

class RssSpider(XMLFeedSpider):
	name = 'rss'
	allowed_domains = []
	start_urls = []
	iterator = 'xml'
	itertag = 'item'
	hasTag = []

	for key in dir(Sites):
		value = getattr(Sites, key)
		if type(value) == dict:
			allowed_domains = allowed_domains + value['allowed_domains']
			start_urls = start_urls + value['start_urls']
			if value['hasTag'] == True:
				hasTag.append(*value['allowed_domains'])

	def __init__(self):
		super(RssSpider, self).__init__()
		self.db = MongoClient().bbsRss
		self.collection = self.db.post

	def parse_node(self, response, node):
		description = node.css('description::text').extract()[0]

		for host in self.hasTag:
			if host in response.url:
				description = pyq(description).text()
				break

		post = {
			"channel": response.css('channel > title::text').extract()[0],
			"channelLink": response.css('channel > link::text').extract()[0],
			"title": node.css('title::text').extract()[0],
			"link": node.css('link::text').extract()[0],
			"description": description,
			"category": node.css('category::text').extract()[0],
			"author": node.css('author::text').extract()[0],
		}
		try:
			post['pubDate'] = node.css('pubDate::text').extract()[0]
		except Exception, e:
			post['pubDate'] = node.css('pubdate::text').extract()[0]

		self.collection.update({"url": post['link']}, {"$set": post}, True)