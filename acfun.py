#!/usr/bin/env python

__all__ = ['acfun_download']

import re
from common import *
from iask import iask_download_by_id
from youku import youku_download_by_id
from tudou import tudou_download_by_iid
from qq import qq_download_by_id
import json

def get_srt_json(id):
	url = 'http://comment.acfun.tv/%s.json' % id
	return get_html(url)

def acfun_download_by_id(id, title, merge=True):
	info = json.loads(get_html('http://www.acfun.tv/api/getVideoByID.aspx?vid=' + id))
	t = info['vtype']
	vid = info['vid']
	if t == 'sina':
		iask_download_by_id(vid, title, merge=merge)
	elif t == 'youku':
		youku_download_by_id(vid, title, merge=merge)
	elif t == 'tudou':
		tudou_download_by_iid(vid, title, merge=merge)
	elif t == 'qq':
		qq_download_by_id(vid, title, merge=merge)
	else:
		raise NotImplementedError(t)

	srt = get_srt_json(vid)
	with open(title + '.json', 'w') as x:
		x.write(srt)

def acfun_download(url, merge=True):
	assert re.match(r'http://www.acfun.tv/v/ac(\d+)', url)
	html = get_html(url).decode('utf-8')

	title = r1(r'<h1 id="title-article" class="title"[^<>]*>([^<>]+)<span', html)
	assert title
	title = unescape_html(title)
	title = escape_file_path(title)
	title = title.replace(' - AcFun.tv', '')

	id = r1(r"\[[Vv]ideo\](\d+)\[/[Vv]ideo\]", html)
	if id:
		return acfun_download_by_id(id, title, merge=merge)
	id = r1(r'<embed [^<>]* src="[^"]+id=(\d+)[^"]+"', html)
	assert id
	iask_download_by_id(id, title, merge=merge)



download = acfun_download
download_playlist = playlist_not_supported('acfun')

def main():
	script_main('acfun', acfun_download)

if __name__ == '__main__':
	main()

