import InlineWorker from 'inline-worker';

export class Jamming {
	config = {
		sampleRate: 48000,
		frameSize: 100, /* in ms */
	};

	constructor(source, cfg) {
		Object.assign(this.config, cfg)
/* ================ START THREAD ================ */
		this.worker = new InlineWorker(function() {
			let recBuffers = [];
			this.onmessage = function(e) {
				switch (e.data.command) {
				}
			}
		});
/* ================ END THREAD ================ */
	}

	async start() {
	}
};

export default Jamming;
