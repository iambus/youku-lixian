
import urllib2
import os.path
import sys
import re

default_encoding = sys.getfilesystemencoding()
if default_encoding.lower() == 'ascii':
	default_encoding = 'utf-8'

def to_native_string(s):
	if type(s) == unicode:
		return s.encode(default_encoding)
	else:
		return s

def r1(pattern, text):
	m = re.search(pattern, text)
	if m:
		return m.group(1)

def r1_of(patterns, text):
	for p in patterns:
		x = r1(p, text)
		if x:
			return x

def unescape_html(html):
	import xml.sax.saxutils
	html = xml.sax.saxutils.unescape(html)
	html = re.sub(r'&#(\d+);', lambda x: unichr(int(x.group(1))), html)
	return html

def ungzip(s):
	from StringIO import StringIO
	import gzip
	buffer = StringIO(s)
	f = gzip.GzipFile(fileobj=buffer)
	return f.read()

def undeflate(s):
	import zlib
	return zlib.decompress(s, -zlib.MAX_WBITS)

def get_response(url):
	response = urllib2.urlopen(url)
	data = response.read()
	if response.info().get('Content-Encoding') == 'gzip':
		data = ungzip(data)
	elif response.info().get('Content-Encoding') == 'deflate':
		data = undeflate(data)
	response.data = data
	return response

def get_html(url, encoding=None):
	content = get_response(url).data
	if encoding:
		content = content.decode(encoding)
	return content

def get_decoded_html(url):
	response = get_response(url)
	data = response.data
	charset = r1(r'charset=([\w-]+)', response.headers['content-type'])
	if charset:
		return data.decode(charset)
	else:
		return data

def url_save(url, filepath, bar, refer=None):
	headers = {}
	if refer:
		headers['Referer'] = refer
	request = urllib2.Request(url, headers=headers)
	response = urllib2.urlopen(request)
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
	assert received == file_size == os.path.getsize(filepath), '%s == %s == %s' % (received, file_size, os.path.getsize(filepath))

def url_size(url):
	request = urllib2.Request(url)
	request.get_method = lambda: 'HEAD'
	response = urllib2.urlopen(request)
	size = int(response.headers['content-length'])
	return size

def url_size(url):
	size = int(urllib2.urlopen(url).headers['content-length'])
	return size

def urls_size(urls):
	return sum(map(url_size, urls))

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
		percent = self.received*100.0/self.total_size
		if percent > 100:
			percent = 100.0
		bar_rate = 100.0 / bar_size
		dots = percent / bar_rate
		dots = int(dots)
		plus = percent / bar_rate - dots
		if plus > 0.8:
			plus = '='
		elif plus > 0.4:
			plus = '-'
		else:
			plus = ''
		bar = '=' * dots + plus
		bar = '{0:>3.0f}% [{1:<40}] {2}/{3}'.format(percent, bar, self.current_piece, self.total_pieces)
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

class PiecesProgressBar:
	def __init__(self, total_size, total_pieces=1):
		self.displayed = False
		self.total_size = total_size
		self.total_pieces = total_pieces
		self.current_piece = 1
		self.received = 0
	def update(self):
		self.displayed = True
		bar = '{0:>3}%[{1:<40}] {2}/{3}'.format('?', '?'*40, self.current_piece, self.total_pieces)
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

class DummyProgressBar:
	def __init__(self, *args):
		pass
	def update_received(self, n):
		pass
	def update_piece(self, n):
		pass
	def done(self):
		pass

def escape_file_path(path):
	path = path.replace('/', '-')
	path = path.replace('\\', '-')
	path = path.replace('*', '-')
	path = path.replace('?', '-')
	return path

def download_urls(urls, title, ext, total_size, output_dir='.', refer=None, merge=True):
	assert urls
	assert ext in ('flv', 'mp4')
	if not total_size:
		try:
			total_size = urls_size(urls)
		except:
			import traceback
			import sys
			traceback.print_exc(file=sys.stdout)
			pass
	title = to_native_string(title)
	title = escape_file_path(title)
	filename = '%s.%s' % (title, ext)
	filepath = os.path.join(output_dir, filename)
	if total_size:
		if os.path.exists(filepath) and os.path.getsize(filepath) >= total_size * 0.9:
			print 'Skip %s: file already exists' % filepath
			return
		bar = SimpleProgressBar(total_size, len(urls))
	else:
		bar = PiecesProgressBar(total_size, len(urls))
	if len(urls) == 1:
		url = urls[0]
		print 'Downloading %s ...' % filename
		url_save(url, filepath, bar, refer=refer)
		bar.done()
	else:
		flvs = []
		print 'Downloading %s.%s ...' % (title, ext)
		for i, url in enumerate(urls):
			filename = '%s[%02d].%s' % (title, i, ext)
			filepath = os.path.join(output_dir, filename)
			flvs.append(filepath)
			#print 'Downloading %s [%s/%s]...' % (filename, i+1, len(urls))
			bar.update_piece(i+1)
			url_save(url, filepath, bar, refer=refer)
		bar.done()
		if not merge:
			return
		if ext == 'flv':
			from flv_join import concat_flvs
			concat_flvs(flvs, os.path.join(output_dir, title+'.flv'))
			for flv in flvs:
				os.remove(flv)
		elif ext == 'mp4':
			from mp4_join import concat_mp4s
			concat_mp4s(flvs, os.path.join(output_dir, title+'.mp4'))
			for flv in flvs:
				os.remove(flv)
		else:
			print "Can't join %s files" % ext

def playlist_not_supported(name):
	def f(*args, **kwargs):
		raise NotImplementedError('Play list is not supported for '+name)
	return f

def script_main(script_name, download, download_playlist=None):
	if download_playlist:
		help = 'python %s.py [--playlist] [-c|--create-dir] [--no-merge] url ...' % script_name
		short_opts = 'hc'
		opts = ['help', 'playlist', 'create-dir', 'no-merge']
	else:
		help = 'python [--no-merge] %s.py url ...' % script_name
		short_opts = 'h'
		opts = ['help', 'no-merge']
	import sys, getopt
	try:
		opts, args = getopt.getopt(sys.argv[1:], short_opts, opts)
	except getopt.GetoptError, err:
		print help
		sys.exit(1)
	playlist = False
	create_dir = False
	merge = True
	for o, a in opts:
		if o in ('-h', '--help'):
			print help
			sys.exit()
		elif o in ('--playlist',):
			playlist = True
		elif o in ('-c', '--create-dir'):
			create_dir = True
		elif o in ('--no-merge'):
			merge = False
		else:
			print help
			sys.exit(1)
	if not args:
		print help
		sys.exit(1)

	for url in args:
		if playlist:
			download_playlist(url, create_dir=create_dir, merge=merge)
		else:
			download(url, merge=merge)

