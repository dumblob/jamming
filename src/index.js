import jamming from './jamming';
import { v4 as uuidv4 } from 'uuid';
import WebSocketAsPromised from 'websocket-as-promised';

/* Deal with MediaStream not having a stop anymore */
/* from: https://stackoverflow.com/a/11646945 */
var MediaStream = window.MediaStream;

if (typeof MediaStream === 'undefined' && typeof webkitMediaStream !== 'undefined') {
    MediaStream = webkitMediaStream;
}

/*global MediaStream:true */
if (typeof MediaStream !== 'undefined' && !('stop' in MediaStream.prototype)) {
    MediaStream.prototype.stop = function() {
        this.getTracks().forEach(function(track) {
            track.stop();
        });
    };
}

function sendServer(obj) {
	let lclobj = Object.assign({}, obj);
	lclobj.uuid = uuid;

	return fetch('/offer', {
		body: JSON.stringify(lclobj),
		headers: {
			'Content-Type': 'application/json'
		},
		method: 'POST'
	    });
}

async function runPage() {
	const uuid = uuidv4();
	const constatus = document.getElementById('constatus');
	const audioSink = document.getElementById('audioSink');
	var stream;
	var wsp;
	var pc;

	const constraints = {
		audio: {
			latency: .005,	/* 5ms latency */
			channelCount: 1,
			noiseSuppression: false,
			autoGainControl: false,
			sampleRate: { min: 22050, max: 48000, ideal: 32000 },
		}
	};

	/* setup local media */
	try {
		stream = await navigator.mediaDevices.getUserMedia(constraints);
	} catch(err) {
		constatus.textContent = 'Unable to open microphone';
		return
	}

	/* setup server messages */
	wsp = new WebSocketAsPromised('ws://' + window.location.host + '/ws', {
		createWebSocket: url => new WebSocket(url),
		extractMessageData: event => event,
	});
	wsp.onError.addListener((err) =>  {
		constatus.textContent = 'connection to server lost';
	});
	wsp.onMessage.addListener((message) => {
		var msg = JSON.parse(message.data);
		console.log('got message via ws:', msg);

		if (msg.uuid == uuid) return;

		if (msg.sdp) {
			pc.setRemoteDescription(new RTCSessionDescription(msg));
		} else if (msg.ice) {
			pc.addIceCandidate(new RTCIceCandidate(msg.ice));
		}
	});
	await wsp.open();
	constatus.textContent = 'connection to server opened';

	function sendServer(obj) {
		var lclobj = Object.assign({}, obj);
		lclobj.uuid = uuid;

		console.log('send:', lclobj);
		wsp.send(JSON.stringify(lclobj));
	}

	/* we are initiator */
	const configuration = {
		iceServers: [ {
			urls: [
				'stun:stun3.l.google.com:19302',
				/* reduce number of stun servers
				'stun:stun.l.google.com:19302',
				'stun:stun1.l.google.com:19302',
				'stun:stun2.l.google.com:19302',
				'stun:stun4.l.google.com:19302',
				*/
				'stun:stun.services.mozilla.com',
			]
		} ]
	};
	pc = new RTCPeerConnection(configuration);
	pc.onicecandidate = (event) => {
		if (event.candidate != null) {
			console.log(event.candidate)
			sendServer({ ice: event.candidate });
		}
	};
	pc.ontrack = (event) => {
		audioSink.srcObject = event.streams[0];
		constatus.textContent = 'playing audio';
	};
	pc.addStream(stream);

	try {
		var desc = await pc.createOffer()
	} catch(err) {
		constatus.textContent = 'failed to create offer for server: ' + err;
		return
	}

	/* do description filtering here */

	await pc.setLocalDescription(desc);

	var ld = pc.localDescription;
	sendServer({ sdp: ld.sdp, type: ld.type });

	async function stopEverything() {
		constatus.textContent = 'a';
		stream.stop();
		constatus.textContent = 'b';
		var v = wsp.close();
		constatus.textContent = 'c';
		pc.close();
		constatus.textContent = 'd';
		await v;
		constatus.textContent = 'Stopped';
	};

	global.stopPage = () => {
		constatus.textContent = 'pa';
		stopEverything();
	}
}
runPage()

// #4 of https://stackoverflow.com/questions/37656592/define-global-variable-with-webpack
global.runPage = runPage;

async function foo() {
	var cert = await RTCPeerConnection.generateCertificate({
		name: "ECDSA", namedCurve: "P-256",
		hash: 'SHA-256'
	});
	// global.pc = new RTCPeerConnection({certificates: [cert]});
}

async function bar() {
	const signaling = new SignalingChannel(); // handles JSON.stringify/parse
	const configuration = {
		iceServers: [ {
			urls: [
				'stun.l.google.com:19302',
				'stun1.l.google.com:19302',
				'stun2.l.google.com:19302',
				'stun3.l.google.com:19302',
				'stun4.l.google.com:19302',
				'stun:stun.services.mozilla.com',
			]
		} ]
	};

	let pc, channel;

	// call start() to initiate
	function start() {
		pc = new RTCPeerConnection(configuration);

		// send any ice candidates to the other peer
		pc.onicecandidate = ({candidate}) => signaling.send({candidate});

		// let the "negotiationneeded" event trigger offer generation
		pc.onnegotiationneeded = async () => {
			try {
				await pc.setLocalDescription();
				// send the offer to the other peer
				signaling.send({description: pc.localDescription});
			} catch (err) {
				console.error(err);
			}
		};

		// create data channel and setup chat using "negotiated" pattern
		channel = pc.createDataChannel('chat', {negotiated: true, id: 0});
		channel.onopen = () => input.disabled = false;
		channel.onmessage = ({data}) => showChatMessage(data);

		input.onkeypress = ({keyCode}) => {
			// only send when user presses enter
			if (keyCode != 13) return;
			channel.send(input.value);
		}
	}

	signaling.onmessage = async ({data: {description, candidate}}) => {
		if (!pc) start(false);

		try {
			if (description) {
				await pc.setRemoteDescription(description);
				// if we got an offer, we need to reply with an answer
				if (description.type == 'offer') {
					await pc.setLocalDescription();
					signaling.send({description: pc.localDescription});
				}
			} else if (candidate) {
				await pc.addIceCandidate(candidate);
			}
		} catch (err) {
			console.error(err);
		}
	};
}
