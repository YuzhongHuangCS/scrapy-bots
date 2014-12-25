# -*- coding: utf-8 -*-
from scrapy.http import Request
from scrapy.spider import Spider
import sqlite3
import json

class RankSpider(Spider):
	name = 'rank'
	allowed_domains = ['eastmoney.com']
	start_urls = []

	def __init__(self, *args, **kwargs):
		super(RankSpider, self).__init__(*args, **kwargs)
		self.db = sqlite3.connect('data.db')
		self.cursor = self.db.cursor()
		self.cursor.execute('CREATE TABLE IF NOT EXISTS Stock (id VARCHAR(6) PRIMARY KEY, name TEXT, plate TEXT)')
		self.db.commit()

	def start_requests(self):
		plateUrl = 'http://hq2data.eastmoney.com/bk/data/trade.js'
		yield Request(plateUrl, callback=self.parsePlateList)

	def parsePlateList(self, response):
		body = response.body.decode('gb2312', 'ignore')
		left = body.index('[[')
		right = body.index(']]') + 2
		plateList = json.loads(body[left:right])[0]
		for plate in plateList:
			plate = plate.split(',')
			stockUrl = 'http://hqdigi2.eastmoney.com/EM_Quote2010NumericApplication/index.aspx?type=s&sortType=C&sortRule=-1&pageSize=10000000&page=1&jsName=quote&style=28002%s' % plate[9]
			metaData = {
				"plate": plate[0] 
			}
			yield Request(stockUrl, callback=self.parseStockList, meta=metaData, dont_filter=True)
	
	def parseStockList(self, response):
		left = response.body.index('[')
		right = response.body.index(']') + 1
		stockList = json.loads(response.body[left:right])
		
		for stock in stockList:
			stock = stock.split(',')
			id = stock[0][:-1]
			name = stock[2]
			plate = response.meta['plate']
			self.cursor.execute('INSERT OR REPLACE INTO Stock (id, name, plate) VALUES (?, ?, ?)', (id, name, plate))

		self.db.commit()