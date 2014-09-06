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

	shangyuluntan = {
		"allowed_domains": ['shangyuluntan.com'],
		"start_urls": ['http://shangyuluntan.com/forum.php?mod=rss&fid=%s' % i for i in range(0, 10)],
		"hasTag": False
	}

	sy0575 = {
		"allowed_domains": ['0575sy.com'],
		"start_urls": ['http://bbs.0575sy.com/rss.php?fid-%s.html' % i for i in range(0, 200)],
		"hasTag": False
	}

	cejbbs = {
		"allowed_domains": ['cejbbs.com'],
		"start_urls": ['http://www.cejbbs.com/forum.php?mod=rss&fid=%s' % i for i in range(0, 100)],
		"hasTag": False
	}