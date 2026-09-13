import re

with open('scripts_dev/prism_source.js', encoding='utf-8') as f:
    code = f.read()

matches = re.findall(r'"([^"]+)"', code)
plugins = [m for m in matches if 'plugin' in m.lower()]
print('Plugin matches:', set(plugins))

langs = [m for m in matches if 'lang' in m.lower()]
print('Lang matches:', set(langs))

print('\nAll properties / string literals containing path or load:')
others = [m for m in matches if any(k in m.lower() for k in ['path', 'load', 'registry', 'http', 'esm', 'prism'])]
print('Others:', set(others))
