#!/usr/bin/env python

import urllib2
import json
from random import randint
from time import time
import re
import os.path
import shutil
import sys

def get_html(url):
	return urllib2.urlopen(url).read()

def r1(pattern, text):
	m = re.match(pattern, text)
	if m:
		return m.group(1)

def r1_of(patterns, text):
	for p in patterns:
		x = r1(p, text)
		if x:
			return x

def find_video_id_from_url(url):
	patterns = [r'http://v.youku.com/v_show/id_([\w=]+).html',
	            r'http://player.youku.com/player.php/sid/([\w=]+)/v.swf',
	            r'loader\.swf\?VideoIDS=([\w=]+)',
				r'^([\w=]+)$']
	return r1_of(patterns, url)

def find_video_id_from_show_page(url):
	return re.search(r'<div class="btnplay">.*href="([^"]+)"', get_html(url)).group(1)

def youku_url(url):
	id = find_video_id_from_url(url)
	if id:
		return 'http://v.youku.com/v_show/id_%s.html' % id
	if re.match(r'http://www.youku.com/show_page/id_\w+.html', url):
		return find_video_id_from_show_page(url)
	if re.match(r'http://v.youku.com/v_playlist/\w+.html', url):
		return url
	raise Exception('Invalid youku URL: '+url)

def parse_page(url):
	url = youku_url(url)
	page = get_html(url)
	id2 = re.search(r"var\s+videoId2\s*=\s*'(\S+)'", page).group(1)
	if re.search(r'v_playlist', url):
		# if we are playing a viedo from play list, the meta title might be incorrect
		title = re.search(r'<title>([^<>]*)</title>', page).group(1).decode('utf-8')
	else:
		title = re.search(r'<meta name="title" content="([^"]*)">', page).group(1).decode('utf-8')
	title = title.replace(u' - \u89c6\u9891 - \u4f18\u9177\u89c6\u9891 - \u5728\u7ebf\u89c2\u770b', '').strip()
	if re.search(r'v_playlist', url) and re.search(r'-.*\S+', title):
		title = re.sub(r'^[^-]+-\s*', '', title) # remove the special name from title for playlist video
	subtitle = re.search(r'<span class="subtitle" id="subtitle">([^<>]*)</span>', page)
	if subtitle:
		subtitle = subtitle.group(1).decode('utf-8').strip()
	if subtitle == title:
		subtitle = None
	return id2, title, subtitle

def get_info(videoId2):
	return json.loads(get_html('http://v.youku.com/player/getPlayList/VideoIDS/'+videoId2))

def find_video(info, stream_type=None):
	#key = '%s%x' % (info['data'][0]['key2'], int(info['data'][0]['key1'], 16) ^ 0xA55AA5A5)
	segs = info['data'][0]['segs']
	types = segs.keys()
	if not stream_type:
		for x in ['hd2', 'mp4', 'flv']:
			if x in types:
				stream_type = x
				break
		else:
			raise NotImplementedError()
	assert stream_type in ('hd2', 'mp4', 'flv')
	file_type = {'hd2':'flv', 'mp4':'mp4', 'flv':'flv'}[stream_type]

	seed = info['data'][0]['seed']
	source = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ/\\:._-1234567890")
	mixed = ''
	while source:
		seed = (seed * 211 + 30031) & 0xFFFF
		index = seed * len(source) >> 16
		c = source.pop(index)
		mixed += c

	ids = info['data'][0]['streamfileids'][stream_type].split('*')[:-1]
	vid = ''.join(mixed[int(i)] for i in ids)

	sid = '%s%s%s' % (int(time()*1000), randint(1000, 1999), randint(1000, 9999))

	urls = []
	for s in segs[stream_type]:
		no = '%02x' % int(s['no'])
		url = 'http://f.youku.com/player/getFlvPath/sid/%s_%s/st/%s/fileid/%s%s%s?K=%s&ts=%s' % (sid, no, file_type, vid[:8], no.upper(), vid[10:], s['k'], s['seconds'])
		urls.append((url, int(s['size'])))
	return urls

class SimpleProgressBar:
	def __init__(self, total_size, total_pieces=1):
		self.displayed = False
		self.total_size = total_size
		self.total_pieces = total_pieces
		self.current_piece = 1
		self.received = 0
	def update(self):
		self.displayed = True
		bar_size = 40
		percent = self.received*100/self.total_size
		if percent > 100:
			percent = 100
		dots = bar_size * percent / 100
		plus = percent - dots / bar_size * 100
		if plus > 0.8:
			plus = '='
		elif plus > 0.4:
			plu = '>'
		else:
			plus = ''
		bar = '=' * dots + plus
		bar = '{0:>3}%[{1:<40}] {2}/{3}'.format(percent, bar, self.current_piece, self.total_pieces)
		sys.stdout.write('\r'+bar)
		sys.stdout.flush()
	def update_received(self, n):
		self.received += n
		self.update()
	def update_piece(self, n):
		self.current_piece = n
	def done(self):
		if self.displayed:
			print
			self.displayed = False

def url_save(url, filepath, bar):
	response = urllib2.urlopen(url)
	file_size = int(response.headers['content-length'])
	assert file_size
	if os.path.exists(filepath):
		if file_size == os.path.getsize(filepath):
			if bar:
				bar.done()
			print 'Skip %s: file already exists' % os.path.basename(filepath)
			return
		else:
			if bar:
				bar.done()
			print 'Overwriting', os.path.basename(filepath), '...'
	with open(filepath, 'wb') as output:
		received = 0
		while True:
			buffer = response.read(1024*256)
			if not buffer:
				break
			received += len(buffer)
			output.write(buffer)
			if bar:
				bar.update_received(len(buffer))
	assert received == file_size == os.path.getsize(filepath)

def file_type_of_url(url):
	return str(re.search(r'/st/([^/]+)/', url).group(1))

def youku_download(url, output_dir='', stream_type=None):
	id2, title, subtitle = parse_page(url)
	if subtitle:
		title += '-' + subtitle
	if type(title) == unicode:
		encoding = sys.getfilesystemencoding()
		if encoding.lower() == 'ascii':
			encoding = 'utf-8'
		title = title.encode(encoding)
	info = get_info(id2)
	urls, sizes = zip(*find_video(info, stream_type))
	total_size = sum(sizes)
	bar = SimpleProgressBar(total_size, len(urls))
	assert urls
	if len(urls) == 1:
		url = urls[0]
		filename = '%s.%s' % (title, file_type_of_url(url))
		filepath = os.path.join(output_dir, filename)
		print 'Downloading %s ...' % filename
		url_save(url, filepath, bar)
		bar.done()
	else:
		flvs = []
		file_type = file_type_of_url(urls[0])
		print 'Downloading %s.%s ...' % (title, file_type)
		for i, url in enumerate(urls):
			filename = '%s[%02d].%s' % (title, i, file_type_of_url(url))
			filepath = os.path.join(output_dir, filename)
			flvs.append(filepath)
			#print 'Downloading %s [%s/%s]...' % (filename, i+1, len(urls))
			bar.update_piece(i+1)
			url_save(url, filepath, bar)
		bar.done()
		if file_type == 'flv':
			from flv_join import concat_flvs
			concat_flvs(flvs, os.path.join(output_dir, title+'.flv'))
			for flv in flvs:
				os.remove(flv)
		elif file_type == 'mp4':
			from mp4_join import concat_mp4s
			concat_mp4s(flvs, os.path.join(output_dir, title+'.mp4'))
			for flv in flvs:
				os.remove(flv)
		else:
			print "Can't join %s files" % file_type

def parse_playlist_videos(html):
	return re.findall(r'id="A_(\w+)"', html)

def parse_playlist_pages(html):
	m = re.search(r'<ul class="pages">.*?</ul>', html, flags=re.S)
	if m:
		urls = re.findall(r'href="([^"]+)"', m.group())
		x1, x2, x3 = re.match(r'^(.*page_)(\d+)(_.*)$', urls[-1]).groups()
		return ['http://v.youku.com%s%s%s?__rt=1&__ro=listShow' % (x1, i, x3) for i in range(2, int(x2)+1)]
	else:
		return []

def parse_playlist(url):
	html = get_html(url)
	video_id = re.search(r"var\s+videoId\s*=\s*'(\d+)'", html).group(1)
	show_id = re.search(r'var\s+showid\s*=\s*"(\d+)"', html).group(1)
	list_url = 'http://v.youku.com/v_vpofficiallist/page_1_showid_%s_id_%s.html?__rt=1&__ro=listShow' % (show_id, video_id)
	html = get_html(list_url)
	ids = parse_playlist_videos(html)
	for url in parse_playlist_pages(html):
		ids.extend(parse_playlist_videos(get_html(url)))
	return ids

def parse_vplaylist(url):
	id = r1_of([r'http://www.youku.com/playlist_show/id_(\d+)(?:_ascending_\d_mode_pic(?:_page_\d+)?)?.html',
	            r'http://v.youku.com/v_playlist/f(\d+)o1p\d+.html',
				r'http://u.youku.com/user_playlist/pid_(\d+)_id_[\w=]+(?:_page_\d+)?.html'],
	           url)
	assert id, 'not valid vplaylist url: '+url
	url = 'http://www.youku.com/playlist_show/id_%s.html' % id
	n = int(re.search(r'<span class="num">(\d+)</span>', get_html(url)).group(1))
	return ['http://v.youku.com/v_playlist/f%so1p%s.html' % (id, i) for i in range(n)]

def youku_download_playlist(url):
	if re.match(r'http://www.youku.com/show_page/id_\w+.html', url):
		url = find_video_id_from_show_page(url)
	if re.match(r'http://www.youku.com/playlist_show/id_\d+(?:_ascending_\d_mode_pic(?:_page_\d+)?)?.html', url):
		ids = parse_vplaylist(url)
	elif re.match(r'http://v.youku.com/v_playlist/f\d+o1p\d+.html', url):
		ids = parse_vplaylist(url)
	elif re.match(r'http://u.youku.com/user_playlist/pid_(\d+)_id_[\w=]+(?:_page_\d+)?.html', url):
		ids = parse_vplaylist(url)
	else:
		assert re.match(r'http://v.youku.com/v_show/id_([\w=]+).html', url), 'URL not supported as playlist'
		ids = parse_playlist(url)
	for i, id in enumerate(ids):
		print 'Downloading %s of %s videos...' % (i + 1, len(ids))
		youku_download(id)

def usage():
	print 'python youku.py [--playlist] url ...'

def main():
	import sys, getopt
	try:
		opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "playlist"])
	except getopt.GetoptError, err:
		usage()
		sys.exit(1)
	playlist = False
	for o, a in opts:
		if o in ("-h", "--help"):
			usage()
			sys.exit()
		elif o in ("--playlist",):
			playlist = True
		else:
			usage()
			sys.exit(1)
	if not args:
		usage()
		sys.exit(1)

	for url in args:
		if playlist:
			youku_download_playlist(url)
		else:
			youku_download(url)

if __name__ == '__main__':
	main()

