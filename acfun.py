

import re
from common import *
from iask import iask_download_by_id
from youku import youku_download_by_id

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

	id = r1(r'type=video&amp;id=(\d+)', flashvars)
	if id:
		iask_download_by_id(id, title)
	else:
		id = r1(r'type2=youku&amp;id=(.+)', flashvars)
		if id:
			youku_download_by_id(id, title)
		else:
			raise NotImplementedError(flashvars)

	json = get_srt_json(id)
	with open(title + '.json', 'w') as x:
		x.write(json)

def main():
	script_main('acfun', acfun_download)

if __name__ == '__main__':
	main()

