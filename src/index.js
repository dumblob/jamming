const jamming = require("./jamming");

async function runPage() {
	var constraints = { audio: true };

	let stream = null;

	try {
		stream = await navigator.mediaDevices.getUserMedia(constraints);
		console.log('got stream');
	} catch(err) {
		console.log('got error');
	}
}

// #4 of https://stackoverflow.com/questions/37656592/define-global-variable-with-webpack
global.runPage = runPage;
