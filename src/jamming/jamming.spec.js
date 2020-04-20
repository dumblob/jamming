'use strict'

const Jamming = require('../index')
const expect = require('chai').expect

describe('Jamming class', () => {
	describe('"construct"', () => {
		it('should be instantiable', () => {
			expect(new Jamming()).to.be.an.instanceOf(Jamming);
		})
	})
})
