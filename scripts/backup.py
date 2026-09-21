"""
Backup the LabMS database.

Usage:
    python -m scripts.backup                 # auto-named backup
    python -m scripts.backup --name weekly   # custom suffix

For SQLite → copies the file.
For PostgreSQL → runs pg_dump.
Backups go to ./backups/ directory.
"""
import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime
from urllib.parse import urlparse

from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///database.db')
BACKUP_DIR = os.path.join(os.getcwd(), 'backups')


def _timestamp():
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def backup_sqlite(db_path, name_suffix=''):
    if not os.path.exists(db_path):
        print(f'❌ SQLite database not found: {db_path}')
        sys.exit(1)

    os.makedirs(BACKUP_DIR, exist_ok=True)
    suffix = f'_{name_suffix}' if name_suffix else ''
    out = os.path.join(BACKUP_DIR, f'labms_{_timestamp()}{suffix}.db')

    shutil.copy2(db_path, out)
    size_kb = os.path.getsize(out) / 1024
    print(f'✅ SQLite backup: {out} ({size_kb:.1f} KB)')
    return out


def backup_postgres(url, name_suffix=''):
    parsed = urlparse(url)
    db_name = parsed.path.lstrip('/')
    user = parsed.username
    password = parsed.password
    host = parsed.hostname or 'localhost'
    port = parsed.port or 5432

    os.makedirs(BACKUP_DIR, exist_ok=True)
    suffix = f'_{name_suffix}' if name_suffix else ''
    out = os.path.join(BACKUP_DIR, f'labms_{_timestamp()}{suffix}.sql')

    env = os.environ.copy()
    if password:
        env['PGPASSWORD'] = password

    cmd = [
        'pg_dump',
        '-h', host, '-p', str(port), '-U', user,
        '-F', 'p',  # plain SQL
        '-f', out,
        db_name,
    ]

    print(f'🔄 Running pg_dump → {out}')
    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        if result.returncode != 0:
            print('❌ pg_dump failed:')
            print(result.stderr)
            sys.exit(1)
        size_kb = os.path.getsize(out) / 1024
        print(f'✅ PostgreSQL backup: {out} ({size_kb:.1f} KB)')
        return out
    except FileNotFoundError:
        print('❌ pg_dump not found. Install PostgreSQL client tools.')
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Backup LabMS database')
    parser.add_argument('--name', default='', help='Optional suffix for the backup filename')
    args = parser.parse_args()

    if DATABASE_URL.startswith('sqlite'):
        # Extract path from sqlite:///relative or sqlite:////absolute
        path = DATABASE_URL.replace('sqlite:///', '')
        if not os.path.isabs(path):
            path = os.path.join(os.getcwd(), path)
        backup_sqlite(path, args.name)
    elif DATABASE_URL.startswith('postgresql'):
        backup_postgres(DATABASE_URL, args.name)
    else:
        print(f'❌ Unsupported DATABASE_URL: {DATABASE_URL}')
        sys.exit(1)


if __name__ == '__main__':
    main()