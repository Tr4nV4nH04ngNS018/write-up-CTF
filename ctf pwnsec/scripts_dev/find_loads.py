with open('scripts_dev/prism_source.js', encoding='utf-8') as f:
    code = f.read()

import re
matches = re.finditer(r'\b(load|loadAll)\b', code)
for m in matches:
    pos = m.start()
    print('--- MATCH ---')
    print(code[max(0, pos-80):min(len(code), pos+100)])
