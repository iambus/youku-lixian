#!/usr/bin/env python

__all__ = ['cntv_download', 'cntv_download_by_id']

from common import *
import json
import re

def cntv_download_by_id(id, title=None, output_dir='.', merge=True):
	assert id
	info = json.loads(get_html('http://vdn.apps.cntv.cn/api/getHttpVideoInfo.do?pid='+id).decode('utf-8'))
	title = title or info['title']
	video = info['video']
	alternatives = [x for x in video.keys() if x.startswith('chapters')]
	assert alternatives in (['chapters'], ['chapters', 'chapters2']), alternatives
	chapters = video['chapters2'] if 'chapters2' in video else video['chapters']
	urls = [x['url'] for x in chapters]
	ext = r1(r'\.([^.]+)$', urls[0])
	assert ext in ('flv', 'mp4')
	download_urls(urls, title, str(ext), total_size=None, merge=merge)

def cntv_download(url, merge=True):
	if re.match(r'http://\w+\.cntv\.cn/(\w+/\w+/(classpage/video/)?)?\d+/\d+\.shtml', url):
		id = r1(r'<!--repaste.video.code.begin-->(\w+)<!--repaste.video.code.end-->', get_html(url))
	elif re.match(r'http://xiyou.cntv.cn/v-[\w-]+\.html', url):
		id = r1(r'http://xiyou.cntv.cn/v-([\w-]+)\.html', url)
	else:
		raise NotImplementedError(url)
	cntv_download_by_id(id, merge=merge)

download = cntv_download
download_playlist = playlist_not_supported('cntv')

def main():
	script_main('cntv', cntv_download)

if __name__ == '__main__':
	main()

