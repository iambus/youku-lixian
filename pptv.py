#!/usr/bin/env python

__all__ = ['pptv_download', 'pptv_download_by_id']

import re
import urllib
from common import *
import hashlib

def pptv_download_by_id(id, merge=True):
	xml = get_html('http://web-play.pptv.com/webplay3-151-%s.xml' % id)
	xml = xml.decode('utf-8')
	host = r1(r'<sh>([^<>]+)</sh>', xml)
	port = 8080
	st = r1(r'<st>([^<>]+)</st>', xml)
	key = hashlib.md5(st).hexdigest() # FIXME: incorrect key
	rids = re.findall(r'rid="([^"]+)"', xml)
	rid = r1(r'rid="([^"]+)"', xml)
	title = r1(r'nm="([^"]+)"', xml)
	pieces = re.findall('<sgm no="(\d+)".*fs="(\d+)"', xml)
	numbers, fs = zip(*pieces)
	urls = ['http://%s:%s/%s/%s?key=%s' % (host, port, i, rid, key) for i in numbers]
	urls = ['http://pptv.vod.lxdns.com/%s/%s?key=%s' % (i, rid, key) for i in numbers]
	total_size = sum(map(int, fs))
	assert rid.endswith('.mp4')
	download_urls(urls, title, 'mp4', total_size=total_size, merge=merge)

def pptv_download(url, merge=True):
	assert re.match(r'http://v.pptv.com/show/(\w+)\.html$', url)
	html = get_html(url)
	id = r1(r'webcfg\s*=\s*{"id":\s*(\d+)', html)
	assert id
	pptv_download_by_id(id, merge=merge)

download = pptv_download
download_playlist = playlist_not_supported('pptv')

def main():
	script_main('pptv', pptv_download)

if __name__ == '__main__':
	main()

