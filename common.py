
import urllib2
import os.path
import sys

def get_html(url):
	response = urllib2.urlopen(url)
	data = response.read()
	if response.info().get('Content-Encoding') == 'gzip':
		from StringIO import StringIO
		import gzip
		buf = StringIO(data)
		f = gzip.GzipFile(fileobj=buf)
		data = f.read()
	return data


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

def url_size(url):
	request = urllib2.Request(url)
	request.get_method = lambda: 'HEAD'
	response = urllib2.urlopen(request)
	size = int(response.headers['content-length'])
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

def download_urls(urls, title, ext, total_size, output_dir='.'):
	assert urls
	assert ext in ('flv', 'mp4')
	if not total_size:
		total_size = urls_size(urls)
	bar = SimpleProgressBar(total_size, len(urls))
	if len(urls) == 1:
		url = urls[0]
		filename = '%s.%s' % (title, ext)
		filepath = os.path.join(output_dir, filename)
		print 'Downloading %s ...' % filename
		url_save(url, filepath, bar)
		bar.done()
	else:
		flvs = []
		file_type = ext
		print 'Downloading %s.%s ...' % (title, file_type)
		for i, url in enumerate(urls):
			filename = '%s[%02d].%s' % (title, i, ext)
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

