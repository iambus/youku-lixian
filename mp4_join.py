
# reference: c041828_ISO_IEC_14496-12_2005(E).pdf

import struct
from cStringIO import StringIO

def skip(stream, n):
	stream.seek(stream.tell() + n)

def skip_zeros(stream, n):
	assert stream.read(n) == '\x00' * n

def read_int(stream):
	return struct.unpack('>i', stream.read(4))[0]

def read_uint(stream):
	return struct.unpack('>I', stream.read(4))[0]

def write_uint(stream, n):
	stream.write(struct.pack('>I', n))

def read_ushort(stream):
	return struct.unpack('>H', stream.read(2))[0]

def read_ulong(stream):
	return struct.unpack('>Q', stream.read(8))[0]

def read_byte(stream):
	return ord(stream.read(1))

def copy_stream(source, target, n):
	buffer_size = 1024*1024
	while n > 0:
		to_read = min(buffer_size, n)
		s = source.read(to_read)
		assert len(s) == to_read, 'no enough data'
		target.write(s)
		n -= to_read

class Atom:
	def __init__(self, type, size, body):
		assert len(type) == 4
		self.type = type
		self.size = size
		self.body = body
	def __str__(self):
		return '<Atom(%s):%s>' % (self.type, repr(self.body))
	def __repr__(self):
		return str(self)
	def write1(self, stream):
		#print self.type, stream.tell()
		write_uint(stream, self.size)
		stream.write(self.type)
	def write(self, stream):
		assert type(self.body) in (str, list), '%s: %s' % (self.type, type(self.body))
		if type(self.body) == str:
			assert self.size == 8 + len(self.body)
			self.write1(stream)
			stream.write(self.body)
		else:
			self.write1(stream)
			for atom in self.body:
				atom.write(stream)

def read_raw(stream, size, left, type):
	assert size == left + 8
	body = stream.read(left)
	return Atom(type, size, body)

def read_body_stream(stream, left):
	body = stream.read(left)
	assert len(body) == left
	return body, StringIO(body)

def read_full_atom(stream):
	value = read_uint(stream)
	version = value >> 24
	flags = value & 0xffffff
	assert version == 0
	return value

def read_mvhd(stream, size, left, type):
	body, stream = read_body_stream(stream, left)
	value = read_full_atom(stream)
	left -= 4

	# new Date(movieTime * 1000 - 2082850791998L); 
	creation_time = read_uint(stream)
	modification_time = read_uint(stream)
	time_scale = read_uint(stream)
	duration = read_uint(stream)
	left -= 16

	qt_preferred_fate = read_uint(stream)
	qt_preferred_volume = read_ushort(stream)
	assert stream.read(10) == '\x00' * 10
	qt_matrixA = read_uint(stream)
	qt_matrixB = read_uint(stream)
	qt_matrixU = read_uint(stream)
	qt_matrixC = read_uint(stream)
	qt_matrixD = read_uint(stream)
	qt_matrixV = read_uint(stream)
	qt_matrixX = read_uint(stream)
	qt_matrixY = read_uint(stream)
	qt_matrixW = read_uint(stream)
	qt_previewTime = read_uint(stream)
	qt_previewDuration = read_uint(stream)
	qt_posterTime = read_uint(stream)
	qt_selectionTime = read_uint(stream)
	qt_selectionDuration = read_uint(stream)
	qt_currentTime = read_uint(stream)
	nextTrackID = read_uint(stream)
	left -= 80
	assert left == 0
	return Atom('mvhd', size, body)

def read_tkhd(stream, size, left, type):
	body, stream = read_body_stream(stream, left)
	value = read_full_atom(stream)
	left -= 4

	# new Date(movieTime * 1000 - 2082850791998L); 
	creation_time = read_uint(stream)
	modification_time = read_uint(stream)
	track_id = read_uint(stream)
	assert stream.read(4) == '\x00' * 4
	duration = read_uint(stream)
	left -= 20

	assert stream.read(8) == '\x00' * 8
	qt_layer = read_ushort(stream)
	qt_alternate_group = read_ushort(stream)
	qt_volume = read_ushort(stream)
	assert stream.read(2) == '\x00\x00'
	qt_matrixA = read_uint(stream)
	qt_matrixB = read_uint(stream)
	qt_matrixU = read_uint(stream)
	qt_matrixC = read_uint(stream)
	qt_matrixD = read_uint(stream)
	qt_matrixV = read_uint(stream)
	qt_matrixX = read_uint(stream)
	qt_matrixY = read_uint(stream)
	qt_matrixW = read_uint(stream)
	qt_track_width = read_uint(stream)
	width = qt_track_width >> 16
	qt_track_height = read_uint(stream)
	height = qt_track_height >> 16
	left -= 60
	assert left == 0
	return Atom('tkhd', size, body)

def read_mdhd(stream, size, left, type):
	body, stream = read_body_stream(stream, left)
	value = read_full_atom(stream)
	left -= 4

	# new Date(movieTime * 1000 - 2082850791998L); 
	creation_time = read_uint(stream)
	modification_time = read_uint(stream)
	time_scale = read_uint(stream)
	duration = read_uint(stream)
	left -= 16

	packed_language = read_ushort(stream)
	qt_quality = read_ushort(stream)
	left -= 4

	assert left == 0
	return Atom('mdhd', size, body)

def read_hdlr(stream, size, left, type):
	body, stream = read_body_stream(stream, left)
	value = read_full_atom(stream)
	left -= 4

	qt_component_type = read_uint(stream)
	handler_type = read_uint(stream)
	qt_component_manufacturer = read_uint(stream)
	qt_component_flags = read_uint(stream)
	qt_component_flags_mask = read_uint(stream)
	left -= 20

	track_name = stream.read(left - 1)
	assert stream.read(1) == '\x00'

	return Atom('hdlr', size, body)

def read_vmhd(stream, size, left, type):
	body, stream = read_body_stream(stream, left)
	value = read_full_atom(stream)
	left -= 4

	assert left == 8
	graphic_mode = read_ushort(stream)
	op_color_read = read_ushort(stream)
	op_color_green = read_ushort(stream)
	op_color_blue = read_ushort(stream)

	return Atom('vmhd', size, body)

def read_stsd(stream, size, left, type):
	value = read_full_atom(stream)
	left -= 4

	entry_count = read_uint(stream)
	left -= 4

	children = []
	for i in range(entry_count):
		atom = read_atom(stream)
		children.append(atom)
		left -= atom.size

	assert left == 0
	#return Atom('stsd', size, children)
	class stsd_atom(Atom):
		def __init__(self, type, size, body):
			Atom.__init__(self, type, size, body)
		def write(self, stream):
			self.write1(stream)
			write_uint(stream, self.body[0])
			write_uint(stream, len(self.body[1]))
			for atom in self.body[1]:
				atom.write(stream)
	return stsd_atom('stsd', size, (value, children))

def read_avc1(stream, size, left, type):
	body, stream = read_body_stream(stream, left)

	skip_zeros(stream, 6)
	data_reference_index = read_ushort(stream)
	skip_zeros(stream, 2)
	skip_zeros(stream, 2)
	skip_zeros(stream, 12)
	width = read_ushort(stream)
	height = read_ushort(stream)
	horizontal_rez = read_uint(stream) >> 16
	vertical_rez = read_uint(stream) >> 16
	assert stream.read(4) == '\x00' * 4
	frame_count = read_ushort(stream)
	string_len = read_byte(stream)
	compressor_name = stream.read(31)
	depth = read_ushort(stream)
	assert stream.read(2) == '\xff\xff'
	left -= 78

	child = read_atom(stream)
	assert child.type == 'avcC', 'if the sub atom is not avcC, you should not cache raw body'
	left -= child.size
	stream.read(left) # XXX
	return Atom('avc1', size, body)

def read_avcC(stream, size, left, type):
	stream.read(left)
	return Atom('avcC', size, None)

def read_stts(stream, size, left, type):
	value = read_full_atom(stream)
	left -= 4

	entry_count = read_uint(stream)
	left -= 4

	samples = []
	for i in range(entry_count):
		sample_count = read_uint(stream)
		sample_duration = read_uint(stream)
		samples.append((sample_count, sample_duration))
		left -= 8
	
	assert left == 0
	#return Atom('stts', size, None)
	class stts_atom(Atom):
		def __init__(self, type, size, body):
			Atom.__init__(self, type, size, body)
		def write(self, stream):
			self.write1(stream)
			write_uint(stream, self.body[0])
			write_uint(stream, len(self.body[1]))
			for sample_count, sample_duration in self.body[1]:
				write_uint(stream, sample_count)
				write_uint(stream, sample_duration)
	return stts_atom('stts', size, (value, samples))

def read_stss(stream, size, left, type):
	value = read_full_atom(stream)
	left -= 4

	entry_count = read_uint(stream)
	left -= 4

	samples = []
	for i in range(entry_count):
		sample = read_uint(stream)
		samples.append(sample)
		left -= 4
	
	assert left == 0
	#return Atom('stss', size, None)
	class stss_atom(Atom):
		def __init__(self, type, size, body):
			Atom.__init__(self, type, size, body)
		def write(self, stream):
			self.write1(stream)
			write_uint(stream, self.body[0])
			write_uint(stream, len(self.body[1]))
			for sample in self.body[1]:
				write_uint(stream, sample)
	return stss_atom('stss', size, (value, samples))

def read_stsc(stream, size, left, type):
	value = read_full_atom(stream)
	left -= 4

	entry_count = read_uint(stream)
	left -= 4

	chunks = []
	for i in range(entry_count):
		first_chunk = read_uint(stream)
		samples_per_chunk = read_uint(stream)
		sample_description_index = read_uint(stream)
		assert sample_description_index == 1 # what is it?
		chunks.append((first_chunk, samples_per_chunk, sample_description_index))
		left -= 12
	#chunks, samples = zip(*chunks)
	#total = 0
	#for c, s in zip(chunks[1:], samples):
	#	total += c*s
	#print 'total', total
	
	assert left == 0
	#return Atom('stsc', size, None)
	class stsc_atom(Atom):
		def __init__(self, type, size, body):
			Atom.__init__(self, type, size, body)
		def write(self, stream):
			self.write1(stream)
			write_uint(stream, self.body[0])
			write_uint(stream, len(self.body[1]))
			for first_chunk, samples_per_chunk, sample_description_index in self.body[1]:
				write_uint(stream, first_chunk)
				write_uint(stream, samples_per_chunk)
				write_uint(stream, sample_description_index)
	return stsc_atom('stsc', size, (value, chunks))

def read_stsz(stream, size, left, type):
	value = read_full_atom(stream)
	left -= 4

	sample_size = read_uint(stream)
	sample_count = read_uint(stream)
	left -= 8

	assert sample_size == 0
	total = 0
	sizes = []
	if sample_size == 0:
		for i in range(sample_count):
			entry_size = read_uint(stream)
			sizes.append(entry_size)
			total += entry_size
			left -= 4

	assert left == 0
	#return Atom('stsz', size, None)
	class stsz_atom(Atom):
		def __init__(self, type, size, body):
			Atom.__init__(self, type, size, body)
		def write(self, stream):
			self.write1(stream)
			write_uint(stream, self.body[0])
			write_uint(stream, self.body[1])
			write_uint(stream, self.body[2])
			for entry_size in self.body[3]:
				write_uint(stream, entry_size)
	return stsz_atom('stsz', size, (value, sample_size, sample_count, sizes))

def read_stco(stream, size, left, type):
	value = read_full_atom(stream)
	left -= 4

	entry_count = read_uint(stream)
	left -= 4

	offsets = []
	for i in range(entry_count):
		chunk_offset = read_uint(stream)
		offsets.append(chunk_offset)
		left -= 4
	
	assert left == 0
	#return Atom('stco', size, None)
	class stco_atom(Atom):
		def __init__(self, type, size, body):
			Atom.__init__(self, type, size, body)
		def write(self, stream):
			self.write1(stream)
			write_uint(stream, self.body[0])
			write_uint(stream, len(self.body[1]))
			for chunk_offset in self.body[1]:
				write_uint(stream, chunk_offset)
	return stco_atom('stco', size, (value, offsets))

def read_smhd(stream, size, left, type):
	body, stream = read_body_stream(stream, left)
	value = read_full_atom(stream)
	left -= 4

	balance = read_ushort(stream)
	assert stream.read(2) == '\x00\x00'
	left -= 4

	assert left == 0
	return Atom('smhd', size, body)

def read_mp4a(stream, size, left, type):
	body, stream = read_body_stream(stream, left)

	assert stream.read(6) == '\x00' * 6
	data_reference_index = read_ushort(stream)
	assert stream.read(8) == '\x00' * 8
	channel_count = read_ushort(stream)
	sample_size = read_ushort(stream)
	assert stream.read(4) == '\x00' * 4
	time_scale = read_ushort(stream)
	assert stream.read(2) == '\x00' * 2
	left -= 28

	atom = read_atom(stream)
	assert atom.type == 'esds'
	left -= atom.size

	assert left == 0
	return Atom('mp4a', size, body)

def read_descriptor(stream):
	tag = read_byte(stream)
	raise NotImplementedError()

def read_esds(stream, size, left, type):
	value = read_uint(stream)
	version = value >> 24
	assert version == 0
	flags = value & 0xffffff
	left -= 4

	body = stream.read(left)
	return Atom('esds', size, None)

def read_composite_atom(stream, size, left, type):
	children = []
	while left > 0:
		atom = read_atom(stream)
		children.append(atom)
		left -= atom.size
	assert left == 0, left
	return Atom(type, size, children)

def read_mdat(stream, size, left, type):
	source_start = stream.tell()
	source_size = left
	skip(stream, left)
	#return Atom(type, size, None)
	#raise NotImplementedError()
	class mdat_atom(Atom):
		def __init__(self, type, size, body):
			Atom.__init__(self, type, size, body)
		def write(self, stream):
			source, source_start, source_size = self.body
			original = source.tell()
			source.seek(source_start)
			self.write1(stream)
			copy_stream(source, stream, source_size)
	return mdat_atom('mdat', size, (stream, source_start, source_size))

atom_readers = {
	'mvhd': read_mvhd, # merge duration
	'tkhd': read_tkhd, # merge duration
	'mdhd': read_mdhd, # merge duration
	'hdlr': read_hdlr, # nothing
	'vmhd': read_vmhd, # nothing
	'stsd': read_stsd, # nothing
	'avc1': read_avc1, # nothing
	'avcC': read_avcC, # nothing
	'stts': read_stts, # sample_count, sample_duration
	'stss': read_stss, # join indexes
	'stsc': read_stsc, # merge # records
	'stsz': read_stsz, # merge # samples
	'stco': read_stco, # merge # chunks
	'smhd': read_smhd, # nothing
	'mp4a': read_mp4a, # nothing
	'esds': read_esds, # noting

	'ftyp': read_raw,
	'yqoo': read_raw,
	'moov': read_composite_atom,
	'trak': read_composite_atom,
	'mdia': read_composite_atom,
	'minf': read_composite_atom,
	'dinf': read_composite_atom,
	'stbl': read_composite_atom,
	'iods': read_raw,
	'dref': read_raw,
	'ctts': read_raw,
	'free': read_raw,
	'edts': read_raw,

	'mdat': read_mdat,
}
#stsd sample descriptions (codec types, initialization etc.) 
#stts (decoding) time-to-sample  
#ctts (composition) time to sample 
#stsc sample-to-chunk, partial data-offset information 
#stsz sample sizes (framing) 
#stz2 compact sample sizes (framing) 
#stco chunk offset, partial data-offset information 
#co64 64-bit chunk offset 
#stss sync sample table (random access points) 
#stsh shadow sync sample table 
#padb sample padding bits 
#stdp sample degradation priority 
#sdtp independent and disposable samples 
#sbgp sample-to-group 
#sgpd sample group description 
#subs sub-sample information


def read_atom(stream):
	n = 0
	size = read_uint(stream)
	assert size > 0
	n += 4
	type = stream.read(4)
	n += 4
	assert type != 'uuid'
	if size == 1:
		size = read_ulong(stream)
		n += 8

	left = size - n
	if type in atom_readers:
		return atom_readers[type](stream, size, left, type)
	raise NotImplementedError('%s: %d' % (type, left))

def write_atom(stream, atom):
	atom.write(stream)



