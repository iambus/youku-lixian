
import re
from common import *

def video_info(id):
	xml = get_decoded_html('http://v.iask.com/v_play.php?vid=%s' % id)
	urls = re.findall(r'<url>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</url>', xml)
	name = r1(r'<vname>(?:<!\[CDATA\[)?(.+?)(?:\]\]>)?</vname>', xml)
	vstr = r1(r'<vstr>(?:<!\[CDATA\[)?(.+?)(?:\]\]>)?</vstr>', xml)
	return urls, name, vstr

def iask_download_by_id(id, title=None):
	urls, name, vstr = video_info(id)
	title = title or name
	assert title
	download_urls(urls, title, 'flv', total_size=None)

def iask_download(url):
	id = r1(r'vid:(\d+),', get_html(url))
	iask_download_by_id(id)

def main():
	script_main('iask', iask_download)

if __name__ == '__main__':
	main()

