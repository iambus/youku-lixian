

import urllib2
import re
from common import *


def parse_video_info(xml):
	urls = re.findall(r'<url>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</url>', xml)
	vstr = re.search(r'<vstr>(?:<!\[CDATA\[)?(.+?)(?:\]\]>)?</vstr>', xml).group(1)
	return urls, vstr

def video_info(id):
	xml = urllib2.urlopen('http://v.iask.com/v_play.php?vid=%s'%id).read()
	return parse_video_info(xml)

def get_srt_json(id):
	url = 'http://comment.acfun.tv/%s.json' % id
	return get_html(url)

def acfun_download(url):
	assert re.match(r'http://www.acfun.tv/v/ac(\d+)', url)
	html = get_html(url)
	title = re.search(r'<title>([^<>]+)</title>', html).group(1).decode('gbk')
	title = unescape_html(title)
	title = title.replace(' - AcFun.tv', '')
	id = re.search(r'flashvars="[^"]*id=(\d+)"', html).group(1)
	urls, vstr = video_info(id)
	download_urls(urls, title, 'flv', total_size=None)
	json = get_srt_json(id)
	with open(title + '.json', 'w') as x:
		x.write(json)

def usage():
	print 'python acfun.py url ...'

def main():
	import sys, getopt
	try:
		opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
	except getopt.GetoptError, err:
		usage()
		sys.exit(1)
	for o, a in opts:
		if o in ("-h", "--help"):
			usage()
			sys.exit()
		else:
			usage()
			sys.exit(1)
	if not args:
		usage()
		sys.exit(1)

	for url in args:
		acfun_download(url)

if __name__ == '__main__':
	main()

