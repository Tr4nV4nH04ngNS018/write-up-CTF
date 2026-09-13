const path = require('path');
const { JSDOM } = require(path.resolve(__dirname, '..', 'challenge_mouse', 'app', 'node_modules', 'jsdom'));
const dom = new JSDOM('<a id="x" href="data:text/javascript,console.log(1337)">');
const doc = dom.window.document;
const a = doc.getElementById('x');
console.log('a.toString():', a.toString());
console.log('String(a):', String(a));
