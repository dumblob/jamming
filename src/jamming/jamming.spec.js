'use strict'

const Jamming = require('../jamming').Jamming
const expect = require('chai').expect

describe('Jamming class', () => {
	describe('"construct"', () => {
		it('should be instantiable', () => {
			expect(new Jamming()).to.be.an.instanceOf(Jamming);
		})
	})
})
