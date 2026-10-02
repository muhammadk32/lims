"""
Revisit adjustments:
1. Remove the revisit banner
2. Do NOT pre-select tests (leave test panel empty)
3. Keep patient fields pre-filled (only)
"""
p = 'static/js/reception.js'
s = open(p, encoding='utf-8').read()

if 'REVISIT_NO_TESTS' in s:
    print('SKIP - already patched')
else:
    # Find the test pre-selection block and disable it
    old_tests = '''    if (data.tests && data.tests.length && typeof addTest === 'function') {
      data.tests.forEach(function (t) {
        var already = state.selectedTests.some(function (x) { return x.id === t.id; });
        if (already) return;
        addTest({
          id: t.id,
          code: t.code,
          name: t.name,
          price: t.price,
          is_panel: t.is_panel,
          parameter_count: t.parameter_count || 0,
        });
      });
    }'''

    new_tests = '''    // ===== REVISIT_NO_TESTS =====
    // Do NOT pre-select tests on revisit. Reception picks fresh.'''

    if old_tests in s:
        s = s.replace(old_tests, new_tests, 1)
        open(p, 'w', encoding='utf-8').write(s)
        print('OK  - test pre-select disabled')
    else:
        print('WARN - test pre-select block not found')

# Remove banner from template
tp = 'modules/orders/templates/orders/new.html'
t = open(tp, encoding='utf-8').read()

if 'revisit-banner' in t:
    import re
    # Remove the entire {% if revisit_order ... %} ... {% endif %} block
    pattern = re.compile(
        r'\{%\s*if revisit_order and prefill_patient\s*%\}.*?\{%\s*endif\s*%\}',
        re.DOTALL,
    )
    t_new, n = pattern.subn('', t, count=1)
    if n:
        t = t_new
        print('OK  - banner removed from template')
    else:
        print('WARN - banner pattern not matched')

    # Also remove any leftover revisit-banner div
    t = t.replace('  <div class="revisit-banner" id="revisitBanner">', '')
    t = t.replace('</div>\n  {% endif %}', '')

    with open(tp, 'w', encoding='utf-8') as f:
        f.write(t)
else:
    print('SKIP - no banner in template')

print()
print('=' * 50)
print('Restart Flask and hard-refresh.')
print('=' * 50)
