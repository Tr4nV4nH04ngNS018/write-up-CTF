const path = require('path');
const { JSDOM } = require(path.resolve(__dirname, '..', 'challenge_mouse', 'app', 'node_modules', 'jsdom'));
const DOMPurify = require(path.resolve(__dirname, '..', 'challenge_mouse', 'app', 'node_modules', 'dompurify'))(new JSDOM('').window);

function renderText(text) {
  return DOMPurify.sanitize(String(text), { ALLOWED_TAGS: [], ALLOWED_ATTR: [] });
}

console.log('1:', JSON.stringify(renderText('</title><p data-prism-plugins>')));
console.log('2:', JSON.stringify(renderText('"> <p data-prism-plugins>')));
console.log('3:', JSON.stringify(renderText('test <div data-prism-plugins> hello')));
