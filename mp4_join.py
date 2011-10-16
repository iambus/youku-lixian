
# reference: c041828_ISO_IEC_14496-12_2005(E)

import struct

def skip(stream, n):
	stream.seek(stream.tell() + n)

def skip_zeros(stream, n):
	assert stream.read(n) == '\x00' * n

def read_int(stream):
	return struct.unpack('>i', stream.read(4))[0]

def read_uint(stream):
	return struct.unpack('>I', stream.read(4))[0]

def read_ushort(stream):
	return struct.unpack('>H', stream.read(2))[0]

def read_ulong(stream):
	return struct.unpack('>Q', stream.read(8))[0]

def read_byte(stream):
	return ord(stream.read(1))

def type_to_int(type):
	return struct.unpack('>I', type)

def int_to_type(n):
	return struct.pack('>I', n)

MP4ExtendedAtomType = type_to_int('uuid')

class Atom:
	def __init__(self, type, size, body):
		self.type = type
		self.size = size
		self.body = body
	def __str__(self):
		return '<Atom(%s):%s>' % (self.type, repr(self.body))
	def __repr__(self):
		return str(self)

def read_mvhd(stream, size, left):
	value = read_uint(stream)
	version = value >> 24
	flags = value & 0xffffff
	left -= 4

	assert version == 0
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
	return Atom('mvhd', size, None)

def read_tkhd(stream, size, left):
	value = read_uint(stream)
	version = value >> 24
	flags = value & 0xffffff
	left -= 4

	assert version == 0
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
	return Atom('tkhd', size, None)

def read_mdhd(stream, size, left):
	value = read_uint(stream)
	version = value >> 24
	flags = value & 0xffffff
	left -= 4

	assert version == 0
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
	return Atom('mdhd', size, None)

def read_hdlr(stream, size, left):
	value = read_uint(stream)
	version = value >> 24
	flags = value & 0xffffff
	left -= 4

	assert value == 0

	qt_component_type = read_uint(stream)
	handler_type = read_uint(stream)
	qt_component_manufacturer = read_uint(stream)
	qt_component_flags = read_uint(stream)
	qt_component_flags_mask = read_uint(stream)
	left -= 20

	track_name = stream.read(left - 1)
	assert stream.read(1) == '\x00'

	return Atom('hdlr', size, None)

def read_vmhd(stream, size, left):
	value = read_uint(stream)
	version = value >> 24
	flags = value & 0xffffff
	left -= 4

	assert version == 0

	assert left == 8
	graphic_mode = read_ushort(stream)
	op_color_read = read_ushort(stream)
	op_color_green = read_ushort(stream)
	op_color_blue = read_ushort(stream)

	return Atom('vmhd', size, None)

def read_stsd(stream, size, left):
	value = read_uint(stream)
	version = value >> 24
	flags = value & 0xffffff
	left -= 4

	assert version == 0

	entry_count = read_uint(stream)
	left -= 4

	children = []
	for i in range(entry_count):
		atom = read_atom(stream)
		children.append(atom)
		left -= atom.size

	assert left == 0
	return Atom('stsd', size, children)

def read_avc1(stream, size, left):
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
	left -= child.size
	stream.read(left) # XXX
	return Atom('avc1', size, child)

def read_avcC(stream, size, left):
	stream.read(left)
	return Atom('avcC', size, None)

def read_stts(stream, size, left):
	value = read_uint(stream)
	version = value >> 24
	flags = value & 0xffffff
	left -= 4

	assert version == 0

	entry_count = read_uint(stream)
	left -= 4

	for i in range(entry_count):
		sample_count = read_uint(stream)
		sample_duration = read_uint(stream)
		left -= 8
	
	assert left == 0
	return Atom('stts', size, None)

def read_stss(stream, size, left):
	value = read_uint(stream)
	version = value >> 24
	flags = value & 0xffffff
	left -= 4

	assert version == 0

	entry_count = read_uint(stream)
	left -= 4

	for i in range(entry_count):
		sample = read_uint(stream)
		left -= 4
	
	assert left == 0
	return Atom('stss', size, None)

def read_stsc(stream, size, left):
	value = read_uint(stream)
	version = value >> 24
	flags = value & 0xffffff
	left -= 4

	assert version == 0

	entry_count = read_uint(stream)
	left -= 4

	for i in range(entry_count):
		first_chunk = read_uint(stream)
		samples_per_chunk = read_uint(stream)
		sample_description_index = read_uint(stream)
		left -= 12
	
	assert left == 0
	return Atom('stsc', size, None)

def read_stsz(stream, size, left):
	value = read_uint(stream)
	version = value >> 24
	flags = value & 0xffffff
	left -= 4

	assert version == 0

	sample_size = read_uint(stream)
	sample_count = read_uint(stream)
	left -= 8

	assert sample_size == 0
	if sample_size == 0:
		for i in range(sample_count):
			some_size = read_uint(stream) # XXX: what size?
			left -= 4

	assert left == 0
	return Atom('stsz', size, None)

def read_stco(stream, size, left):
	value = read_uint(stream)
	version = value >> 24
	flags = value & 0xffffff
	left -= 4

	assert version == 0

	entry_count = read_uint(stream)
	left -= 4

	for i in range(entry_count):
		chunk_offset = read_uint(stream)
		left -= 4
	
	assert left == 0
	return Atom('stco', size, None)

def read_smhd(stream, size, left):
	value = read_uint(stream)
	version = value >> 24
	assert version == 0
	flags = value & 0xffffff
	left -= 4

	balance = read_ushort(stream)
	assert stream.read(2) == '\x00\x00'
	left -= 4

	assert left == 0
	return Atom('smhd', size, None)

def read_mp4a(stream, size, left):
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
	left -= atom.size

	assert left == 0
	return Atom('mp4a', size, atom)

def read_descriptor(stream):
	tag = read_byte(stream)
	raise NotImplementedError()

def read_esds(stram, size, left):
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
	'stsc': read_stsc, # merge
	'stsz': read_stsz, # merge
	'stco': read_stco, # merge
	'smhd': read_smhd, # nothing
	'mp4a': read_mp4a, # nothing
	'esds': read_esds, # noting
}

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
	if type in ('ftyp', 'yqoo'):
		return Atom(type, size, stream.read(left))
	if type in ('moov', 'trak', 'mdia', 'minf', 'dinf', 'stbl'):
		return read_composite_atom(stream, size, left, type)
	if type in atom_readers:
		return atom_readers[type](stream, size, left)
	if type in ('iods', 'dref', 'ctts', 'mdat', 'free', 'edts'):
	#if type in ('iods', 'dref', 'ctts', 'mdat', 'edts', 'free'):
		# XXX
		#print type, size
		skip(stream, left)
		return Atom(type, size, None)
		#return Atom(type, size, stream.read(left))
		#print type, repr(stream.read(left))
		#return Atom(type, size, None)
	raise NotImplementedError('%s: %d' % (type, left))

def write_atom(stream, atom):
	raise NotImplementedError()


