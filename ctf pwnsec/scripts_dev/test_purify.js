const path = require('path');
const appDir = path.resolve(__dirname, '..', 'challenge_mouse', 'app');
const { JSDOM } = require(path.join(appDir, 'node_modules', 'jsdom'));
const DOMPurify = require(path.join(appDir, 'node_modules', 'dompurify'))(new JSDOM('').window);

function renderText(text) {
  return DOMPurify.sanitize(String(text), { ALLOWED_TAGS: [], ALLOWED_ATTR: [] });
}
console.log('Test 1:', JSON.stringify(renderText('<p data-prism-plugins=1>hello</p>')));
console.log('Test 2:', JSON.stringify(renderText('foo<b>bar</b>baz')));
console.log('Test 3:', JSON.stringify(renderText('</title><div data-prism-plugins=1>')));
console.log('Test 4:', JSON.stringify(renderText('plain text & < > "')));
