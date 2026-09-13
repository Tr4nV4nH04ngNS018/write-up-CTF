import subprocess

code = """
const { JSDOM } = require('jsdom');
const dom = new JSDOM('', { url: 'http://127.0.0.1:3000/notes/123' });
const win = dom.window;

for (const prop of Object.getOwnPropertyNames(win)) {
    if (prop.length <= 4) {
        console.log(prop, typeof win[prop]);
    }
}
"""

with open('scripts_dev/list_props.js', 'w') as f:
    f.write(code)

import os
app_dir = os.path.abspath('challenge_mouse/app')
p = subprocess.run(['node', 'scripts_dev/list_props.js'], cwd=app_dir, capture_output=True, text=True)
print(p.stdout)
