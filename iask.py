
import re
from common import *

def video_info(id):
	xml = get_html('http://v.iask.com/v_play.php?vid=%s' % id)
	urls = re.findall(r'<url>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</url>', xml)
	vstr = re.search(r'<vstr>(?:<!\[CDATA\[)?(.+?)(?:\]\]>)?</vstr>', xml).group(1)
	return urls, vstr


