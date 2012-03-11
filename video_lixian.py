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

from common import *
import re

def url_to_module(url):
	site = r1(r'http://([^/]+)/', url)
	assert site, 'invalid url: ' + url
	domain = r1(r'(\.[^.]+\.[^.]+)$', site)
	assert domain, 'not supported url: ' + url
	k = r1(r'([^.]+)', domain)
	downloads = {
			'youku':youku,
			'bilibili':bilibili,
			'acfun':acfun,
			'iask':iask,
			'ku6':ku6,
			'pptv':pptv,
			'iqiyi':iqiyi,
			'tudou':tudou,
			'sohu':sohu,
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


