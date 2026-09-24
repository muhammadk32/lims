# Move Lab Test Settings to top-level, right AFTER Administration
p = 'templates/layout/topnav.html'
t = open(p, encoding='utf-8').read()

import re

# 1. Remove the Lab Test Settings link from inside Administration dropdown
t2, n = re.subn(
    r'\s*<a\s+href="[^"]*settings/tests/formats"[^>]*>.*?Lab Test Settings.*?</a>',
    '',
    t,
    count=1,
    flags=re.DOTALL,
)
if n:
    t = t2
    print('OK  - removed from Administration dropdown')
else:
    print('WARN - Lab Test Settings link not found in dropdown')

# 2. Find the Administration nav block end (its </div> right after the dropdown)
# Anchor: the closing of Administration's topnav-item div
# We search for the last </div> before the closing of the nav-container, after 'Administration'

# Simpler: find the closing comment or a known-end pattern
# Look for the last 'Administration' occurrence and jump to the closing '</div>' group

admin_idx = t.rfind('Administration')
if admin_idx == -1:
    print('ERR - Administration nav not found')
else:
    # From admin_idx, find the next '</div>\n    </div>' — this closes the topnav-item
    # then insert our link after that
    search_from = admin_idx
    end_idx = t.find('{% endif %}', search_from)
    if end_idx == -1:
        print('ERR - endif after Administration not found')
    else:
        # Find the </div> that closes the topnav-item right before {% endif %}
        insert_after = t.find('</div>', end_idx)  # closing topnav-dropdown? skip
        # Actually: after {% endif %} we want to add our new link.
        # Move insert point to just after {% endif %} line
        line_end = t.find('\n', end_idx) + 1

        new_block = '''
    {# Lab Test Settings (admin only) #}
    {% if current_user.role == 'admin' %}
    <a href="{{ url_for('test_settings.formats') }}"
       class="topnav-link {% if request.path.startswith('/settings/tests') %}active{% endif %}">
      <i class="bi bi-sliders2"></i><span>Lab Test Settings</span>
    </a>
    {% endif %}
'''
        t = t[:line_end] + new_block + t[line_end:]
        print('OK  - Lab Test Settings inserted after Administration')

        with open(p, 'w', encoding='utf-8') as f:
            f.write(t)
        print('OK  - topnav saved')

# 3. Verify
s = open(p, encoding='utf-8').read()
count_formats = s.count('settings/tests/formats')
print()
print('Verify:')
print('  Lab Test Settings links in topnav:', count_formats)
