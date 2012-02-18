
from common import *

def tudou_download_by_iid(iid, title):
	xml = get_html('http://v2.tudou.com/v?it=' + iid)

	from xml.dom.minidom import parseString
	doc = parseString(xml)
	title = title or doc.firstChild.getAttribute('tt') or doc.firstChild.getAttribute('title')
	urls = [(int(n.getAttribute('brt')), n.firstChild.nodeValue.strip()) for n in doc.getElementsByTagName('f')]

	url = max(urls, key=lambda x:x[0])[1]
	assert 'f4v' in url

	#url_save(url, filepath, bar):
	download_urls([url], title, 'flv', total_size=None)

def tudou_download_by_id(id, title):
	html = get_html('http://www.tudou.com/programs/view/%s/' % id)
	iid = r1(r'iid\s*=\s*(\S+)', html)
	tudou_download_by_iid(iid, title)


