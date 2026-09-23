# Fix discount amount input — don't overwrite the field the user is typing in
p = 'static/js/reception.js'
s = open(p, encoding='utf-8').read()

old = """      if (pctInput && roundedSubtotal > 0) {
        const pct = (discountValue / roundedSubtotal) * 100;
        pctInput.value = pct.toFixed(2);
      } else if (pctInput) {
        pctInput.value = '0';
      }
      if (amtInput) amtInput.value = roundMoney(discountValue).toFixed(2);"""

new = """      if (pctInput && roundedSubtotal > 0) {
        const pct = (discountValue / roundedSubtotal) * 100;
        pctInput.value = pct.toFixed(2);
      } else if (pctInput) {
        pctInput.value = '0';
      }
      // Do NOT write back to amtInput — the user is typing in it.
      // Overwriting it kills the cursor position and prevents multi-digit entry."""

if old in s:
    s = s.replace(old, new, 1)
    open(p, 'w', encoding='utf-8').write(s)
    print('OK  - reception.js: discount amount no longer self-overwrites')
elif 'Do NOT write back to amtInput' in s:
    print('SKIP - already fixed')
else:
    print('WARN - pattern not found — searching...')
    for i, line in enumerate(s.split(chr(10)), 1):
        if 'amtInput.value' in line and 'roundMoney' in line:
            print(f'  {i}: {line.strip()}')
