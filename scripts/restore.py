"""
Restore LabMS database from a backup file.

Usage:
    python -m scripts.restore backups/labms_20250115_143022.db

⚠️  DANGER: This overwrites the current database. Confirmation is required.
"""
import argparse
import os
import shutil
import subprocess
import sys
from urllib.parse import urlparse

from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///database.db')


def restore_sqlite(db_path, backup_path):
    if not os.path.exists(backup_path):
        print(f'❌ Backup file not found: {backup_path}')
        sys.exit(1)

    # Safety: back up current DB first
    if os.path.exists(db_path):
        safety = f'{db_path}.pre_restore'
        shutil.copy2(db_path, safety)
        print(f'🛡️  Safety copy of current DB: {safety}')

    shutil.copy2(backup_path, db_path)
    print(f'✅ Restored SQLite from {backup_path}')


def restore_postgres(url, backup_path):
    if not os.path.exists(backup_path):
        print(f'❌ Backup file not found: {backup_path}')
        sys.exit(1)

    parsed = urlparse(url)
    db_name = parsed.path.lstrip('/')
    user = parsed.username
    password = parsed.password
    host = parsed.hostname or 'localhost'
    port = parsed.port or 5432

    env = os.environ.copy()
    if password:
        env['PGPASSWORD'] = password

    cmd = [
        'psql', '-h', host, '-p', str(port), '-U', user,
        '-d', db_name, '-f', backup_path,
    ]

    print(f'🔄 Running psql < {backup_path}')
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if result.returncode != 0:
        print('❌ Restore failed:')
        print(result.stderr)
        sys.exit(1)
    print(f'✅ Restored PostgreSQL from {backup_path}')


def main():
    parser = argparse.ArgumentParser(description='Restore LabMS database')
    parser.add_argument('backup', help='Path to backup file')
    parser.add_argument('--yes', action='store_true', help='Skip confirmation')
    args = parser.parse_args()

    if not args.yes:
        print(f'⚠️  This will OVERWRITE the current database.')
        print(f'   Backup file: {args.backup}')
        confirm = input('Type "yes" to continue: ').strip().lower()
        if confirm != 'yes':
            print('Cancelled.')
            return

    if DATABASE_URL.startswith('sqlite'):
        path = DATABASE_URL.replace('sqlite:///', '')
        if not os.path.isabs(path):
            path = os.path.join(os.getcwd(), path)
        restore_sqlite(path, args.backup)
    elif DATABASE_URL.startswith('postgresql'):
        restore_postgres(DATABASE_URL, args.backup)
    else:
        print(f'❌ Unsupported DATABASE_URL: {DATABASE_URL}')
        sys.exit(1)


if __name__ == '__main__':
    main()