"""
Fix mojibake (double-encoded UTF-8) in all HTML templates.
Reads file bytes, finds common double-encoded sequences, writes back clean UTF-8.
"""
import os

# Common UTF-8 characters that got double-encoded by saving as ANSI/Latin-1
# Format: (mojibake_bytes, correct_utf8_bytes)
FIXES = [
    # Middle dot: ·
    (b'\xc3\x82\xc2\xb7', b'\xc2\xb7'),
    # Em dash: —
    (b'\xc3\xa2\xe2\x82\xac\xe2\x80\x9d', b'\xe2\x80\x94'),
    (b'\xc3\xa2\xe2\x82\xac\xe2\x80\x9c', b'\xe2\x80\x94'),
    # En dash: –
    (b'\xc3\xa2\xe2\x82\xac\xe2\x80\x93', b'\xe2\x80\x93'),
    # Bullet: •
    (b'\xc3\xa2\xe2\x82\xac\xc2\xa2', b'\xe2\x80\xa2'),
    (b'\xc3\xa2\xe2\x82\xac\xe2\x80\xa2', b'\xe2\x80\xa2'),
    # Ellipsis: …
    (b'\xc3\xa2\xe2\x82\xac\xc2\xa6', b'\xe2\x80\xa6'),
    (b'\xc3\xa2\xe2\x82\xac\xe2\x80\xa6', b'\xe2\x80\xa6'),
    # Right single quote: '
    (b'\xc3\xa2\xe2\x82\xac\xe2\x84\xa2', b'\xe2\x80\x99'),
    # Left double quote: "
    (b'\xc3\xa2\xe2\x82\xac\xc2\x9c', b'\xe2\x80\x9c'),
    # Right double quote: "
    (b'\xc3\xa2\xe2\x82\xac\xc2\x9d', b'\xe2\x80\x9d'),
    # Accented chars: Ã© → é, etc.
    (b'\xc3\x83\xc2\xa9', b'\xc3\xa9'),
    (b'\xc3\x83\xc2\xa8', b'\xc3\xa8'),
    (b'\xc3\x83\xc2\xa0', b'\xc3\xa0'),
    (b'\xc3\x83\xc2\xa2', b'\xc3\xa2'),
    (b'\xc3\x83\xc2\xa7', b'\xc3\xa7'),
    (b'\xc3\x83\xc2\xb4', b'\xc3\xb4'),
    (b'\xc3\x83\xc2\xb9', b'\xc3\xb9'),
    # Checkbox: ✓ (double-encoded)
    (b'\xc3\xa2\xc5\x93\xe2\x80\x9c', b'\xe2\x9c\x93'),
    # Any remaining â€ (broken dash family)
    (b'\xc3\xa2\xe2\x82\xac', b'\xe2\x80\x94'),   # catch-all
    # Â followed by space or dot
    (b'\xc3\x82', b''),                            # stray Â
    (b'\xc3\xa2\xe2\x82\xac\xc2\xa0', b''),        # stray â€
]

ROOT = 'modules'
EXTRA_ROOTS = ['templates']

def fix_file(path):
    with open(path, 'rb') as f:
        data = f.read()

    original = data
    total = 0
    for old, new in FIXES:
        c = data.count(old)
        if c:
            data = data.replace(old, new)
            total += c

    if data != original:
        with open(path, 'wb') as f:
            f.write(data)
        return total
    return 0

def main():
    total_files = 0
    total_fixes = 0

    roots = [ROOT] + EXTRA_ROOTS
    for root_dir in roots:
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
    print(f'Total: {total_fixes} mojibake sequences fixed across {total_files} files')

if __name__ == '__main__':
    main()
