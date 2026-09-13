const path = require('path');
const { JSDOM } = require(path.resolve(__dirname, '..', 'challenge_mouse', 'app', 'node_modules', 'jsdom'));
const dom = new JSDOM('', { url: 'http://127.0.0.1:3000/notes/123' });
const win = dom.window;

let props = [];
let curr = win;
while (curr) {
    props.push(...Object.getOwnPropertyNames(curr));
    curr = Object.getPrototypeOf(curr);
}

const shortProps = new Set(props.filter(p => p.length <= 4));
console.log('Short props:', [...shortProps].sort());
