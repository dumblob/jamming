'use strict'

const sinon = require('sinon')
const index = require('../index')
const expect = require('chai').expect

var navigator;

function setupBrowser() {
	navigator = {
		mediaDevices: {
			getUserMedia: () => { console.log('dummy'); throw 'failure'; }
		}
	}
	global.navigator = navigator;
}

describe('index module', () => {
	describe('"members"', () => {
		it('should be have the following members', () => {
			expect(global.runPage).to.be.a('function');
		})
	})
	describe('"runPage"', () => {
		it('should call getUserMedia', async () => {
			setupBrowser();

			var gum = sinon.stub(navigator.mediaDevices, 'getUserMedia');
			gum.onFirstCall().returns(true);

			await global.runPage();

			expect(gum.calledOnce).to.be.true;

			gum.restore();
		})
	})
})
