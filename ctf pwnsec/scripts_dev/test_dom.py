import subprocess

cmd = """
const { JSDOM } = require('jsdom');
const DOMPurify = require('dompurify')(new JSDOM('').window);
function renderText(text) {
  return DOMPurify.sanitize(String(text), { ALLOWED_TAGS: [], ALLOWED_ATTR: [] });
}
console.log('1:', JSON.stringify(renderText('<div data-prism-plugins="foo">')));
console.log('2:', JSON.stringify(renderText('test & < > "')));
"""

p = subprocess.run(['node', '-e', cmd], capture_output=True, text=True, cwd='c:/Users/ACER/Downloads/ctf/ctf pwnsec/challenge_mouse/app')
print('STDOUT:', p.stdout)
print('STDERR:', p.stderr)
