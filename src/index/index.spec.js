'use strict'

const index = require('../index')
const expect = require('chai').expect

describe('index module', () => {
	describe('"members"', () => {
		it('should be have the following members', () => {
			expect(global.runPage).to.be.a('function');
		})
	})
})
