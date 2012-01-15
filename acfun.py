

import re
from common import *
from iask import video_info

def get_srt_json(id):
	url = 'http://comment.acfun.tv/%s.json' % id
	return get_html(url)

def acfun_download(url):
	assert re.match(r'http://www.acfun.tv/v/ac(\d+)', url)
	html = get_html(url)
	title = re.search(r'<title>([^<>]+)</title>', html).group(1).decode('gbk')
	title = unescape_html(title)
	title = escape_file_path(title)
	title = title.replace(' - AcFun.tv', '')
	id = re.search(r'flashvars="[^"]*id=(\d+)"', html).group(1)
	urls, vstr = video_info(id)
	download_urls(urls, title, 'flv', total_size=None)
	json = get_srt_json(id)
	with open(title + '.json', 'w') as x:
		x.write(json)

def main():
	script_main('acfun', acfun_download)

if __name__ == '__main__':
	main()

