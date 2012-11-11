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
import yinyuetai
import ifeng

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
			'kankanews':bilibili,
			'smgbb':bilibili,
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
			'yinyuetai':yinyuetai,
			'ifeng':ifeng,
	}
	if k in downloads:
		return downloads[k]
	else:
		raise NotImplementedError(url)

def any_download(url, merge=True):
	m = url_to_module(url)
	m.download(url, merge=merge)

def any_download_playlist(url, create_dir=False, merge=True):
	m = url_to_module(url)
	m.download_playlist(url, create_dir=create_dir, merge=merge)

def main():
	script_main('video_lixian', any_download, any_download_playlist)

if __name__ == '__main__':
	main()


