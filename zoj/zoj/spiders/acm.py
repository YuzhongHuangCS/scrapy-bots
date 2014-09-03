# -*- coding: utf-8 -*-
from scrapy.spider import Spider
from scrapy.contrib.loader import ItemLoader
from zoj.items import Problem
from pyquery import PyQuery as pyq

class AcmSpider(Spider):
    name = "acm"
    allowed_domains = ["acm.zju.edu.cn"]
    start_urls = ['http://acm.zju.edu.cn/onlinejudge/showProblem.do?problemCode=%s' % i for i in range(1001, 3809)]

    def parse(self, response):
        l = ItemLoader(item=Problem(), response=response)
        d = pyq(response.body)
        l.add_value('id', response.url[-4:])
        l.add_value('title', d('#content_body > center:nth-child(1) > span').text())
        l.add_value('body', d('#content_body').text())
        return l.load_item()
