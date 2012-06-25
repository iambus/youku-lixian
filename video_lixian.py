#!/usr/bin/env python

import youku
import bilibili
import acfun
import iask
import ku6
import pptv
import iqiyi
import tudou
import sohu
import w56
import cntv

from common import *
import re

def url_to_module(url):
	site = r1(r'http://([^/]+)/', url)
	assert site, 'invalid url: ' + url
	if site.endswith('.com.cn'):
		site = site[:-3]
	domain = r1(r'(\.[^.]+\.[^.]+)$', site)
	assert domain, 'not supported url: ' + url
	k = r1(r'([^.]+)', domain)
	downloads = {
			'youku':youku,
			'bilibili':bilibili,
			'acfun':acfun,
			'iask':iask,
			'sina':iask,
			'ku6':ku6,
			'pptv':pptv,
			'iqiyi':iqiyi,
			'tudou':tudou,
			'sohu':sohu,
			'56':w56,
			'cntv':cntv,
	}
	if k in downloads:
		return downloads[k]
	else:
		raise NotImplementedError(url)

def any_download(url):
	m = url_to_module(url)
	m.download(url)

def any_download_playlist(url):
	m = url_to_module(url)
	m.download_playlist(url)

def main():
	script_main('video_lixian', any_download, any_download_playlist)

if __name__ == '__main__':
	main()


