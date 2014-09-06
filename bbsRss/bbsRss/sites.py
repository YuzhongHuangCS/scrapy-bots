# -*- coding: utf-8 -*-

# Config sites here

class Sites(object):

	sybbs = {
		"allowed_domains": ['0575bbs.com'],
		"start_urls": ['http://www.0575bbs.com/rss-htm-fid-%s.html' % i for i in range(0, 200)],
		"hasTag": True
	}

	dsybbs = {
		"allowed_domains": ['dsybbs.com'],
		"start_urls": ['http://www.dsybbs.com/forum.php?mod=rss&fid=%s' % i for i in range(0, 300)],
		"hasTag": False
	}