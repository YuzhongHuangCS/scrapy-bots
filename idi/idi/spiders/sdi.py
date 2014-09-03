# -*- coding: utf-8 -*-
from scrapy.http import Request
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from pyquery import PyQuery as pyq
from pymongo import MongoClient
import gridfs

class MainSpider(CrawlSpider):
	name = "sdi"
	allowed_domains = ['www.idi.zju.edu.cn']
	start_urls = ['http://www.idi.zju.edu.cn/blog/']

	rules = (
		Rule(LinkExtractor(allow=('/blog/page/\d*/'), deny=('#!'))),
		Rule(LinkExtractor(allow=('/blog/\d*/\d*/.*/'), deny=('#!')), callback='parsePost'),
		Rule(LinkExtractor(allow=('/blog/.*/'), deny=('#!', '/category/', '/feed/','/tag/', '/author/', '/blog/\d*/')), callback='parsePage'),
	)

	def __init__(self):
		super(MainSpider, self).__init__()
		self.db = MongoClient().idi
		self.postcollection = self.db.post
		self.pageCollection = self.db.page
		self.fs = gridfs.GridFS(self.db)
		self.fsCollection = self.db.fs.files

	def parsePost(self, response):

		def filterRule(url):
			if '/wp-content/uploads/' in url:
				return url 

		d = pyq(response.body)
		post = {
			"url": response.url,
			"title": d('h1.entry-title').text(),
			"category": response.css('span.cat-links > a::text').extract()[0],
			"datetime": response.css('time.entry-date::text').extract()[0],
			"author": response.css('span.vcard > a::text').extract()[0],
			"content":  d('div.entry-content').text(),
			"img": filter(filterRule, response.css('img::attr(src)').extract()),
		}
		self.postcollection.update({"url": post['url']}, post, True)

		# avoid use yield, in order to make attachment download in parallel
		imgs = []
		for url in post['img']:
			imgs.append(Request(url, callback=self.saveImage))

		return imgs

	def parsePage(self, response):
		d = pyq(response.body)
		page = {
			"url": response.url,
			"title": d('h1.entry-title').text(),
			"content":  d('div.entry-content').text(),
		}
		self.pageCollection.update({"url": page['url']}, page, True)

	def saveImage(self, response):
		id = self.fs.put(response.body)
		mime = response.headers['Content-Type']
		self.fsCollection.update({"_id": id}, {'$set': {"url": response.url, "Content-Type": mime}}, True)