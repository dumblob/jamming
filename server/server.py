import aiohttp
import json
import logging
import os.path
import uuid

from aiohttp import web
from aiortc import RTCPeerConnection, RTCIceCandidate, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer

logger = logging.getLogger('pc')
logger.setLevel(logging.INFO)

# Implement https://w3c.github.io/webrtc-pc/#constructor-0 per the
# spec.
from aioice.candidate import Candidate
from aiortc.rtcicetransport import candidate_from_aioice
def RealRTCIceCandidate(candidateInitDict):
	candpref = 'candidate:'
	candstr = candidateInitDict['candidate']
	if not candstr.startswith(candpref):
		raise ValueError('does not start with proper string')
	candstr = candstr[len(candpref):]
	cand = Candidate.from_sdp(candstr)

	ric = candidate_from_aioice(cand)
	ric.sdpMid = candidateInitDict['sdpMid']
	ric.sdpMLineIndex = candidateInitDict['sdpMLineIndex']
	# XXX - exists as part of RTCIceParameters
	#ric.usernameFragment = candidateInitDict['usernameFragment']

	return ric

class AudioMixer(object):
	@property
	def audio(self):
		'''The output audio track for this mixing.'''

	def addTrack(self, track):
		'''Add an import track that will be mixed with
		the other tracks.'''

mixer = AudioMixer()
pcs = set()
shutdown = False

ROOT = os.path.dirname(__file__)

async def index(request):
	content = open(os.path.join(ROOT, '..', 'dist', 'audiotest.html'), 'r').read()
	return web.Response(content_type='text/html', text=content)

async def jammingjs(request):
	content = open(os.path.join(ROOT, '..', 'dist', 'jamming.js'), 'r').read()
	return web.Response(content_type='application/javascript', text=content)

# XXX - update hander to pass uuid and meeting id in the url
async def ws_handler(request):
	ws = web.WebSocketResponse()
	await ws.prepare(request)

	pc_id = str(uuid.uuid4())
	def log_info(msg, *args):
		#print(repr(msg), repr(args))
		# shouldn't be warning, but can't get logging working otherwise
		logger.warning(pc_id + " " + msg, *args)

	log_info("Created for %s", request.remote)

	doexit = False
	async for msg in ws:
		if doexit:
			break

		if msg.type == aiohttp.WSMsgType.TEXT:
			data = json.loads(msg.data)
			log_info('got msg: %s', repr(data))
			if 'sdp' in data:
				offer = RTCSessionDescription(
				    sdp=data['sdp'], type=data['type'])
			elif 'ice' in data:
				pc.addIceCandidate(RealRTCIceCandidate(data['ice']))
				continue

			pc = RTCPeerConnection()

			# add to the currect set
			pcs.add(pc)

			@pc.on("datachannel")
			def on_datachannel(channel):
				@channel.on("message")
				def on_message(message):
					if isinstance(message, str) and message.startswith("ping"):
						channel.send("pong" + message[4:])

			@pc.on("iceconnectionstatechange")
			async def on_iceconnectionstatechange():
				log_info("ICE connection state is %s", pc.iceConnectionState)
				if pc.iceConnectionState == "failed":
					await pc.close()
					pcs.discard(pc)
					doexit = True

			mixer = MediaPlayer('demo-instruct.wav')
			@pc.on("track")
			def on_track(track):
				log_info("Track %s received", track.kind)

				if track.kind == "audio":
					pc.addTrack(mixer.audio)
					#mixer.addTrack(track)

				@track.on("ended")
				async def on_ended():
					log_info("Track %s ended", track.kind)
					# XXX likely not correct
					await mixer.stop()

			log_info("Got offer: %s", repr(offer))

			# handle offer
			await pc.setRemoteDescription(offer)

			# send answer
			answer = await pc.createAnswer()
			await pc.setLocalDescription(answer)

			await ws.send_str(json.dumps({
			    "sdp": pc.localDescription.sdp,
			    "type": pc.localDescription.type,
			}))
		elif msg.type == aiohttp.WSMsgType.ERROR:
			print('ws connection closed with exception %s' %
			    ws.exception())

	print('websocket connection closed')

	return ws

async def on_shutdown(app):
	shutdown = True

	# close peer connections
	coros = [pc.close() for pc in pcs]
	await asyncio.gather(*coros)
	pcs.clear()

def main():
	app = web.Application()
	app.on_shutdown.append(on_shutdown)
	app.router.add_get("/", index)
	app.router.add_get("/jamming.js", jammingjs)
	app.router.add_get("/ws", ws_handler)
	web.run_app(app, access_log=None, port=23854, ssl_context=None)


if __name__ == '__main__':
	main()
