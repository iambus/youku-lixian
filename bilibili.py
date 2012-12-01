#!/usr/bin/env python

__all__ = ['bilibili_download']

import re
from common import *
from iask import iask_download_by_id
from youku import youku_download_by_id
from tudou import tudou_download_by_id

def get_srt_xml(id):
	url = 'http://comment.bilibili.tv/%s.xml' % id
	return get_html(url).decode('utf-8')

def parse_srt_p(p):
	fields = p.split(',')
	assert len(fields) == 8, fields
	time, mode, font_size, font_color, pub_time, pool, user_id, history = fields
	time = float(time)

	mode = int(mode)
	assert 1 <= mode <= 8
	# mode 1~3: scrolling
	# mode 4: bottom
	# mode 5: top
	# mode 6: reverse?
	# mode 7: position
	# mode 8: advanced

	pool = int(pool)
	assert 0 <= pool <= 2
	# pool 0: normal
	# pool 1: srt
	# pool 2: special?
	
	font_size = int(font_size)

	font_color = '#%06x' % int(font_color)

	return pool, mode, font_size, font_color

def parse_srt_xml(xml):
	d = re.findall(r'<d p="([^"]+)">(.*)</d>', xml)
	for x, y in d:
		p = parse_srt_p(x)
	raise NotImplementedError()

def parse_cid_playurl(xml):
	from xml.dom.minidom import parseString
	doc = parseString(xml.encode('utf-8'))
	urls = [durl.getElementsByTagName('url')[0].firstChild.nodeValue for durl in doc.getElementsByTagName('durl')]
	return urls

def bilibili_download_by_cid(id, title, merge=True):
	url = 'http://interface.bilibili.tv/playurl?cid=' + id
	urls = parse_cid_playurl(get_html(url, 'utf-8'))
	if re.search(r'\.(flv|hlv)\b', urls[0]):
		download_urls(urls, title, 'flv', total_size=None, merge=merge)
	elif re.search(r'/mp4/', urls[0]):
		download_urls(urls, title, 'mp4', total_size=None, merge=merge)
	else:
		raise NotImplementedError(urls[0])

def bilibili_download(url, merge=True):
	assert re.match(r'http://(www.bilibili.tv|bilibili.kankanews.com|bilibili.smgbb.cn)/video/av(\d+)', url)
	html = get_html(url)

	title = r1(r'<h2>([^<>]+)</h2>', html).decode('utf-8')
	title = unescape_html(title)
	title = escape_file_path(title)

	flashvars = r1_of([r'flashvars="([^"]+)"', r'"https://secure.bilibili.tv/secure,(cid=\d+)(?:&aid=\d+)?"'], html)
	assert flashvars
	t, id = flashvars.split('=', 1)
	id = id.split('&')[0]
	if t == 'cid':
		bilibili_download_by_cid(id, title, merge=merge)
	elif t == 'vid':
		iask_download_by_id(id, title, merge=merge)
	elif t == 'ykid':
		youku_download_by_id(id, title, merge=merge)
	elif t == 'uid':
		tudou_download_by_id(id, title, merge=merge)
	else:
		raise NotImplementedError(flashvars)

	xml = get_srt_xml(id)
	with open(title + '.xml', 'w') as x:
		x.write(xml.encode('utf-8'))

download = bilibili_download
download_playlist = playlist_not_supported('bilibili')

def main():
	script_main('bilibili', bilibili_download)

if __name__ == '__main__':
	main()

