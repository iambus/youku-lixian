#!/usr/bin/env python

__all__ = ['acfun_download']

import re
from common import *
from iask import iask_download_by_id
from youku import youku_download_by_id
from tudou import tudou_download_by_iid

def get_srt_json(id):
	url = 'http://comment.acfun.tv/%s.json' % id
	return get_html(url)

def acfun_download(url):
	assert re.match(r'http://www.acfun.tv/v/ac(\d+)', url)
	html = get_html(url).decode('gbk')

	title = r1(r'<title>([^<>]+)</title>', html)
	title = unescape_html(title)
	title = escape_file_path(title)
	title = title.replace(' - AcFun.tv', '')

	flashvars = r1(r'flashvars="([^"]+)"', html)

	t, id = flashvars.split('&amp;id=')
	if t == 'type=video':
		iask_download_by_id(id, title)
	elif t == 'type2=youku':
		youku_download_by_id(id, title)
	elif t == 'type2=tudou':
		tudou_download_by_iid(id, title)
	else:
		raise NotImplementedError(flashvars)

	json = get_srt_json(id)
	with open(title + '.json', 'w') as x:
		x.write(json)

download = acfun_download
download_playlist = playlist_not_supported('acfun')

def main():
	script_main('acfun', acfun_download)

if __name__ == '__main__':
	main()

