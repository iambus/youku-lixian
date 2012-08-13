#!/usr/bin/env python

__all__ = ['ku6_download', 'ku6_download_by_id']

import json
import re
from common import *

def ku6_download_by_id(id, title=None, output_dir='.', merge=True):
	data = json.loads(get_html('http://v.ku6.com/fetchVideo4Player/%s...html'%id))['data']
	t = data['t']
	f = data['f']
	size = int(data['videosize'])
	title = title or t
	assert title
	urls = f.split(',')
	ext = re.sub(r'.*\.', '', urls[0])
	assert ext in ('flv', 'mp4', 'f4v'), ext
	ext = {'f4v':'flv'}.get(ext, ext)
	download_urls(urls, title, ext, total_size=size, merge=merge)

def ku6_download(url, merge=True):
	id = r1(r'http://v.ku6.com/special/show_\d+/(.*)\.\.\.html', url)
	ku6_download_by_id(id, merge=merge)

download = ku6_download
download_playlist = playlist_not_supported('ku6')

def main():
	script_main('ku6', ku6_download)

if __name__ == '__main__':
	main()


