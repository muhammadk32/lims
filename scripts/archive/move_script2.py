path = 'modules/orders/templates/orders/new.html'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# Find <script> that contains __REVISIT_DATA
data_start = None
data_end = None
for i, line in enumerate(lines):
    if 'window.__REVISIT_DATA' in line:
        # walk back to find '<script>'
        for k in range(i, max(0, i - 5), -1):
            if '<script>' in lines[k]:
                data_start = k
                break
        break

if data_start is None:
    print('ERR - script start not found')
else:
    for j in range(data_start, min(len(lines), data_start + 60)):
        if '</script>' in lines[j]:
            data_end = j
            break

    if data_end is None:
        print('ERR - script end not found')
    else:
        script_block = lines[data_start:data_end + 1]

        # Remove the block from its current location
        del lines[data_start:data_end + 1]

        # Find the {% endblock %} right BEFORE the original position
        target_endblock = None
        for i in range(data_start - 1, -1, -1):
            if '{% endblock %}' in lines[i]:
                target_endblock = i
                break

        if target_endblock is None:
            print('ERR - no endblock found before script')
        else:
            # Insert script BEFORE that endblock
            for l in reversed(script_block):
                lines.insert(target_endblock, l)
            with open(path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print('OK - script moved inside content block')

# Verify
s = open(path, encoding='utf-8').read()
i1 = s.find('window.__REVISIT_DATA')
i2 = s.find('{% endblock %}', i1)
print('script now before endblock:', i2 != -1)
