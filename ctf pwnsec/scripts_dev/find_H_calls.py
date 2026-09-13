with open('scripts_dev/prism_source.js', encoding='utf-8') as f:
    code = f.read()

import re
matches = re.findall(r'\b[u|h]?e?\("([^"]+)"', code)
print('All string calls in prism_source.js matching e("..."):')
print(matches[:30])

matches_H = re.findall(r'H\("([^"]+)"\)', code)
print('All H("..."):', matches_H)
matches_ue = re.findall(r'ue\("([^"]+)"', code)
print('All ue("..."):', matches_ue)
matches_he = re.findall(r'he\("([^"]+)"', code)
print('All he("..."):', matches_he)
