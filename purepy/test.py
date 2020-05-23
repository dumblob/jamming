#!/usr/bin/env python

from ctypes import c_int, pointer, POINTER, sizeof, c_char, c_uint8, c_int16, cast
from pyogg import opus
from pyogg.opus import opus_int16, opus_int16_p, c_uchar

import array
import functools
import operator
import pyaudio
import queue
import sys
import time
import wave

statusvals = [ 'paInputUnderflow', 'paInputOverflow', 'paOutputUnderflow', 'paOutputOverflow', 'paPrimingOutput' ]
statuses = { getattr(pyaudio, y): y for y in statusvals }

def printstatus(x):
	r = []
	while x:
		b = x & -x	# get a single bit
		r.append(statuses[b])
		x &= ~b		# clear the bit we added

	return ', '.join(r)

rate = 48000
framelength = .0025
maxbw = 128*1024
sampperframe = int(framelength * rate) # 5ms latency

pa = pyaudio.PyAudio()

for i in range(pa.get_device_count()):
	print(i, repr(pa.get_device_info_by_index(i)))

#sys.exit(0)
class _OpusBase(object):
	@staticmethod
	def _check_err(err):
		if err != opus.OPUS_OK:
			raise RuntimeError('failed', err)

class OpusDecoder(_OpusBase):
	def __init__(self, rate, nchan):
		err = c_int()
		self._nchan = nchan
		self._bytespersamp = nchan * sizeof(opus.opus_int16)
		#print('foo:', repr((self._bytespersamp, nchan, sizeof(opus.opus_int16))))
		self._pcmbuf = (opus_int16 * (nchan * int(rate * framelength)))()
		self._dec = opus.opus_decoder_create(rate, nchan, pointer(err))
		self._check_err(err.value)

	def decode(self, frm):
		#print(repr(frm))
		r = opus.opus_decode(self._dec, cast(frm, POINTER(c_uchar)), len(frm), self._pcmbuf, len(self._pcmbuf), 0)
		if r < 0:
			self._check_err(r)

		return array.array('h', self._pcmbuf[:self._nchan * r]).tobytes()

	def __del__(self):
		opus.opus_decoder_destroy(self._dec)
		self._dec = None

class OpusEncoder(_OpusBase):
	def __init__(self, rate, nchan, app):
		err = c_int()
		self._nchan = nchan
		self._bytespersamp = nchan * sizeof(opus.opus_int16)
		#print('bar:', repr((self._bytespersamp, nchan, sizeof(opus.opus_int16))))
		self._frbuf = (c_char * (self._bytespersamp * int(maxbw * framelength)))()
		self._enc = opus.opus_encoder_create(rate, nchan, app, pointer(err))
		self._check_err(err.value)

	def get_max_bw(self):
		val = opus.opus_int32()
		r = opus.opus_encoder_ctl(self._enc, opus.OPUS_GET_MAX_BANDWIDTH, pointer(val))
		self._check_err(r)
		return val.value

	def set_max_bw(self, maxbw):
		r = opus.opus_encoder_ctl(self._enc, opus.OPUS_SET_MAX_BANDWIDTH, opus.opus_int32(maxbw))
		self._check_err(r)

	def get_inband_fec(self):
		val = opus.opus_int32()
		r = opus.opus_encoder_ctl(self._enc, opus.OPUS_GET_INBAND_FEC_REQUEST, pointer(val))
		self._check_err(r)
		return val.value

	def set_inband_fec(self, maxbw):
		r = opus.opus_encoder_ctl(self._enc, opus.OPUS_SET_INBAND_FEC_REQUEST, opus.opus_int32(maxbw))
		self._check_err(r)

	def get_pkt_loss(self):
		val = opus.opus_int32()
		r = opus.opus_encoder_ctl(self._enc, opus.OPUS_GET_PACKET_LOSS_PERC_REQUEST, pointer(val))
		self._check_err(r)
		return val.value

	def set_pkt_loss(self, percent):
		r = opus.opus_encoder_ctl(self._enc, opus.OPUS_SET_PACKET_LOSS_PERC_REQUEST, opus.opus_int32(percent))
		self._check_err(r)

	def encode(self, pcm):
		fs = len(pcm) // self._bytespersamp
		#print(repr(pcm), fs, repr(opus_int16_p), repr(self._nchan))
		#print('baz:', fs, repr((len(pcm), self._bytespersamp)))
		r = opus.opus_encode(self._enc, cast(pcm, opus_int16_p), fs, cast(self._frbuf, POINTER(c_uchar)), len(self._frbuf))
		#r = opus.opus_encode(self._enc, pcm, fs, self._frbuf, len(self._frbuf))
		if r < 0:
			self._check_err(r)

		#print(repr(self._frbuf), dir(self._frbuf))
		return self._frbuf.raw[:r]

	def __del__(self):
		opus.opus_encoder_destroy(self._enc)
		self._enc = None

enc = OpusEncoder(rate, 1, opus.OPUS_APPLICATION_RESTRICTED_LOWDELAY)
dec = OpusDecoder(rate, 1)

enc.set_inband_fec(1)
enc.set_pkt_loss(5)
print('pl:', repr(enc.get_pkt_loss()))
print('if:', repr(enc.get_inband_fec()))

#sys.exit(0)

inbuffer = queue.Queue()
outbufferinfo = []
outbuffer = []
adcdiff = []
dacdiff = []
adcdacdiff = []

times = []

def excprinter(func):
	@functools.wraps(func)
	def func_wrapper(*args, **kwargs):
		global times
		try:
			s = time.time()
			r = func(*args, **kwargs)
			times.append((s, time.time()))
		except:
			import traceback
			traceback.print_exc()
			raise

		return r

	return func_wrapper

#wf = wave.open('foo.wav', 'wb')
#wf.setnchannels(1)
#wf.setsampwidth(2)
#wf.setframerate(rate)

cnt = 0
starttime = None
combstatus = 0

@excprinter
def incallback(in_data, frm_cnt, timeinfo, status):
	inbuffer.put((in_data, frm_cnt, timeinfo, status))

	if time.time() - s < 5:
		return ('', pyaudio.paContinue)

	inbuffer.put(None)	# signal finished
	return ('', pyaudio.paComplete)

def outcallback(in_data, frm_cnt, timeinfo, status):
	outbufferinfo.append((in_data, frm_cnt, timeinfo, status))

	if outbuffer:
		buf = outbuffer.pop(0)
	else:
		buf = '\x00\x00' * sampperframe

	if buf is None:
		return (dbuf, pyaudio.paComplete)

	return (buf, pyaudio.paContinue)

instream = pa.open(rate=rate, channels=1, format=pyaudio.paInt16, input_device_index=0, input=True, frames_per_buffer=sampperframe, stream_callback=incallback)
outstream = pa.open(rate=rate, channels=1, format=pyaudio.paInt16, output_device_index=3, output=True, frames_per_buffer=sampperframe, stream_callback=outcallback)
print('il:', instream.get_input_latency())
print('ol:', outstream.get_output_latency())

s = time.time()

print('starting')
instream.start_stream()
outstream.start_stream()
while True:
	#print('sleep')
	d = inbuffer.get()
	if d is None:
		break
	in_data, frm_cnt, timeinfo, status = d

	combstatus |= status
	if starttime is None:
		starttime = timeinfo
	lasttime = timeinfo

	#print('pcb:', repr((type(in_data), len(in_data), frm_cnt, timeinfo, status)))
	adcdiff.append(timeinfo['current_time'] - timeinfo['input_buffer_adc_time'])
	dacdiff.append(timeinfo['output_buffer_dac_time'] - timeinfo['current_time'])
	adcdacdiff.append(timeinfo['output_buffer_dac_time'] - timeinfo['input_buffer_adc_time'])
	cnt += len(in_data)
	#buf = enc.encode(in_data)
	buf = in_data
	#print('r:', len(buf), repr(buf), repr(type(buf)))
	outbuffer.append(buf)

instream.stop_stream()
outstream.stop_stream()
instream.close()
outstream.close()
print('done')

#print(repr(adcdiff))
#print(repr(dacdiff))
print(max(adcdacdiff), min(adcdacdiff))
print(cnt)
print(starttime)
print(outbufferinfo[0][2])
print(lasttime)
print(outbufferinfo[-1][2])
print(lasttime['current_time'] - starttime['current_time'])
print('in status:', printstatus(combstatus))
print('out status:', printstatus(functools.reduce(operator.__or__, (x[3] for x in outbufferinfo), 0)))
ltimes = [ (e - s) * 1000 for s, e in times ]
print(min(ltimes), max(ltimes))
pa.terminate()
