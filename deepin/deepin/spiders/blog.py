# -*- coding: utf-8 -*-
from scrapy.http import Request
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.loader import ItemLoader
from deepin.items import Post
from pyquery import PyQuery as pyq

class BlogSpider(CrawlSpider):
    name = "blog"
    allowed_domains = ["planet.linuxdeepin.com"]
    start_urls = ['http://planet.linuxdeepin.com/page/%s' % i for i in range(1, 33)]

    rules = (
        Rule(LinkExtractor(allow=('archives/category', ), deny=('author', 'tag'))),
        Rule(LinkExtractor(allow=('archives', )), callback='parsePost'),
    )

    '''
    def parse(self, response):
        for url in response.css('a::attr(href)').extract():
        	if 'archives' in url:
        		if 'category' in url:
        			yield Request(url)
        		else:
        			if 'author' not in url:
        				yield Request(url, callback=self.parsePost)
    '''

    def parsePost(self, response):
    	l = ItemLoader(item=Post(), response=response)
    	d = pyq(response.body)
    	l.add_value('url', response.url)
    	l.add_css('title', 'h1.entry-title::text')
    	l.add_css('date', 'span.entry-date::text')
    	l.add_css('author', 'span.author.vcard > a::text')
    	l.add_value('content', d('div.entry-content').text())
    	
    	return l.load_item()
