!function(t){var e={};function n(r){if(e[r])return e[r].exports;var o=e[r]={i:r,l:!1,exports:{}};return t[r].call(o.exports,o,o.exports,n),o.l=!0,o.exports}n.m=t,n.c=e,n.d=function(t,e,r){n.o(t,e)||Object.defineProperty(t,e,{enumerable:!0,get:r})},n.r=function(t){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(t,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(t,"__esModule",{value:!0})},n.t=function(t,e){if(1&e&&(t=n(t)),8&e)return t;if(4&e&&"object"==typeof t&&t&&t.__esModule)return t;var r=Object.create(null);if(n.r(r),Object.defineProperty(r,"default",{enumerable:!0,value:t}),2&e&&"string"!=typeof t)for(var o in t)n.d(r,o,function(e){return t[e]}.bind(null,o));return r},n.n=function(t){var e=t&&t.__esModule?function(){return t.default}:function(){return t};return n.d(e,"a",e),e},n.o=function(t,e){return Object.prototype.hasOwnProperty.call(t,e)},n.p="",n(n.s=0)}([function(t,e,n){"use strict";t.exports=n(1).Jamming},function(t,e,n){"use strict";Object.defineProperty(e,"__esModule",{value:!0}),e.default=e.Jamming=void 0;var r,o=(r=n(2))&&r.__esModule?r:{default:r};function i(t,e,n){return e in t?Object.defineProperty(t,e,{value:n,enumerable:!0,configurable:!0,writable:!0}):t[e]=n,t}var u=function t(){!function(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),i(this,"otherattr",o.default),i(this,"someattr",5)};e.Jamming=u;var a=u;e.default=a},function(t,e,n){(function(e){var n=!!(e===e.window&&e.URL&&e.Blob&&e.Worker);function r(t,r){var o,i=this;if(r=r||{},n)return o=t.toString().trim().match(/^function\s*\w*\s*\([\w\s,]*\)\s*{([\w\W]*?)}$/)[1],new e.Worker(e.URL.createObjectURL(new e.Blob([o],{type:"text/javascript"})));this.self=r,this.self.postMessage=function(t){setTimeout((function(){i.onmessage({data:t})}),0)},setTimeout(t.bind(r,r),0)}r.prototype.postMessage=function(t){var e=this;setTimeout((function(){e.self.onmessage({data:t})}),0)},t.exports=r}).call(this,n(3))},function(t,e){var n;n=function(){return this}();try{n=n||new Function("return this")()}catch(t){"object"==typeof window&&(n=window)}t.exports=n}]);