web server component -- rendezvous part, and mixing/aggregation

web client component -- connect to server, send encoded data

Meeting setup flow:
	1) Admin uses server to generate room.  The server generates
	   a URL and the admin gives out url to participants.
	   As part of this, restrictions may be applied, such as when
	   the meeting is valid.

Participant flow:
	1) Participant goes to meeting url obtained from admin.
	2) Once meeting is valid, setup the following:
		a) WebRTC data connection to server
		b) Input audio
		c) Output audio
	3) Pass the setup items to do encoding/decoding and playback.


File information:
	src/index.js -- main file for web page

Random references:
navigator.mediaDevices.getSupportedConstraints();
https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getSupportedConstraints
