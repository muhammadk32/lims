path = 'templates/layout/topnav.html'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# ---- 1. Remove the broken block ----
bad_start = None
for i, line in enumerate(lines):
    if '{# Lab Test Settings (admin only) #}' in line:
        bad_start = i
        break

if bad_start is not None:
    bad_end = None
    for j in range(bad_start, min(bad_start + 15, len(lines))):
        if '{% endif %}' in lines[j]:
            bad_end = j
            break
    if bad_end is not None:
        print(f'Removing broken block: lines {bad_start+1}-{bad_end+1}')
        del lines[bad_start:bad_end + 1]

# ---- 2. Remove the dropdown item ----
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    if "url_for('test_settings.formats')" in line and i + 3 < len(lines):
        block = ''.join(lines[i:i+4])
        if 'dropdown-item' in block and 'Lab Test Settings' in block:
            j = i
            while j < len(lines) and '</a>' not in lines[j]:
                j += 1
            skip_to = j + 1
            if skip_to < len(lines) and lines[skip_to].strip() == '':
                skip_to += 1
            print(f'Removing dropdown link: lines {i+1}-{j+1}')
            i = skip_to
            continue
    new_lines.append(line)
    i += 1
lines = new_lines

# ---- 3. Insert top-level link before </nav> ----
for i, line in enumerate(lines):
    if '</nav>' in line:
        insert_block = '''    {# Lab Test Settings (admin only) - top-level #}
    {% if current_user.role == 'admin' %}
    <a href="{{ url_for('test_settings.formats') }}"
       class="topnav-link {% if request.path.startswith('/settings/tests') %}active{% endif %}">
      <i class="bi bi-sliders2"></i><span>Lab Test Settings</span>
    </a>
    {% endif %}

'''
        lines.insert(i, insert_block)
        print(f'OK  - top-level link inserted before </nav> (line {i+1})')
        break

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

s = open(path, encoding='utf-8').read()
print()
print('Verify:')
print('  Lab Test Settings mentions:', s.count('Lab Test Settings'))
