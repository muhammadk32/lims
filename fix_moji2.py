"""
Fix mojibake in all HTML templates — STRING-based replacement.
Reads each file as UTF-8, replaces known bad character sequences,
writes back as clean UTF-8.
"""
import os

# Each pair is (bad_string, good_string) — matched as Unicode chars, not bytes
FIXES = [
    # Middle dot sequences
    ('Â·', '·'),          # U+00C2 + U+00B7 → U+00B7
    ('Â ', ' '),          # Â + space → space
    ('Â',  ''),           # stray Â

    # Em-dash / dash mojibake
    ('â€"', '—'),         # em dash
    ('â€œ', '—'),         # em dash variant
    ('â€“', '–'),         # en dash
    ('â€\x9d', '—'),
    ('â€', '—'),          # leftover

    # Bullet
    ('â€¢', '•'),

    # Ellipsis
    ('â€¦', '…'),

    # Quotes
    ('â€™', "'"),
    ('â€˜', "'"),
    ('â€œ', '"'),
    ('â€\x9c', '"'),

    # Checkbox
    ('âœ"', '✓'),
    ('âœ“', '✓'),
    ('âœ', '✓'),

    # Common emoji mojibake → plain ASCII replacements
    ('ðY"', '[PDF]'),
    ('ðY"', '[PDF]'),
    ('ðY–', '[PRINT]'),
    ('ðY"', '[FILE]'),
    ('ðY', ''),           # any other emoji mojibake → strip

    # Emoji for the print bar
    ('📄', '📄'),         # leave real ones alone
]

def fix_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        return 0

    original = content
    total = 0
    for bad, good in FIXES:
        if bad in content:
            c = content.count(bad)
            content = content.replace(bad, good)
            total += c

    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return total
    return 0

def main():
    total_files = 0
    total_fixes = 0
    for root_dir in ['modules', 'templates']:
        for dirpath, _, filenames in os.walk(root_dir):
            for fn in filenames:
                if fn.endswith('.html'):
                    path = os.path.join(dirpath, fn)
                    n = fix_file(path)
                    if n:
                        print(f'  {path}: {n} fixes')
                        total_files += 1
                        total_fixes += n
    print()
    print(f'Total: {total_fixes} fixes across {total_files} files')

if __name__ == '__main__':
    main()
