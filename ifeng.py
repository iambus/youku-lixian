#!/usr/bin/env python

__all__ = ['ifeng_download', 'ifeng_download_by_id']

from common import *

def ifeng_download_by_id(id, title=None, merge=True):
	assert r1(r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})', id), id
	url = 'http://v.ifeng.com/video_info_new/%s/%s/%s.xml' % (id[-2], id[-2:], id)
	xml = get_html(url, 'utf-8')
	title = r1(r'Name="([^"]+)"', xml)
	title = unescape_html(title)
	url = r1(r'VideoPlayUrl="([^"]+)"', xml)
	from random import randint
	r = randint(10, 19)
	url = url.replace('http://video.ifeng.com/', 'http://video%s.ifeng.com/' % r)
	assert url.endswith('.mp4')
	download_urls([url], title, 'mp4', total_size=None, merge=merge)

def ifeng_download(url, merge=True):
	id = r1(r'/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\.shtml$', url)
	if id:
		return ifeng_download_by_id(id)
	html = get_html(url)
	id = r1(r'var vid="([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"', html)
	assert id, "can't find video info"
	return ifeng_download_by_id(id)

download = ifeng_download
download_playlist = playlist_not_supported('ifeng')

def main():
	script_main('ifeng', ifeng_download)

if __name__ == '__main__':
	main()

