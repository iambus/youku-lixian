
import urllib2
import re
from common import *


def parse_video_info(xml):
	urls = re.findall(r'<url>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</url>', xml)
	vstr = re.search(r'<vstr>(?:<!\[CDATA\[)?(.+?)(?:\]\]>)?</vstr>', xml).group(1)
	return urls, vstr

def video_info(id):
	xml = urllib2.urlopen('http://www.bilibili.tv/v_cdn_play?id=%s'%id).read()
	return parse_video_info(xml)

def bilibili_download(url):
	assert re.match(r'http://www.bilibili.tv/video/av(\d+)', url)
	html = get_html(url)
	title = re.search(r'<h2 id="titles">([^<>]+)<a name="titles">', html).group(1).decode('utf-8')
	id = re.search(r'vid=(\d+)', html).group(1)
	urls, vstr = video_info(id)
	download_urls(urls, title, 'flv', total_size=None)

def usage():
	print 'python bilibili.py url ...'

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
		bilibili_download(url)

if __name__ == '__main__':
	main()

