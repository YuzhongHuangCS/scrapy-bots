# -*- coding: utf-8 -*-

# Scrapy settings for deepin project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'deepin'

SPIDER_MODULES = ['deepin.spiders']
NEWSPIDER_MODULE = 'deepin.spiders'

DEFAULT_ITEM_CLASS = 'deepin.items.Problem'

ITEM_PIPELINES = {
	'deepin.pipelines.StoreToMongoDB': 1
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'deepin (+http://planet.linuxdeepin.com/)'