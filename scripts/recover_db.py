import sqlite3
import shutil
from pathlib import Path
from app.core.config import DATABASE_PATH
# Delay importing init_db because importing app.db.database triggers DB init on import
init_db = None

print(f"Database path: {DATABASE_PATH}")
path = Path(DATABASE_PATH)
if not path.exists():
    print("Database file does not exist; creating new database...")
    try:
        from app.db.database import init_db as _init_db
        _init_db()
        print("Created new database.")
    except Exception as ie:
        print('Failed to initialize DB via SQLAlchemy:', repr(ie))
    raise SystemExit(0)
    raise SystemExit(0)

backup = path.with_suffix('.corrupt.backup')
try:
    conn = sqlite3.connect(str(path))
    cur = conn.cursor()
    cur.execute('PRAGMA integrity_check;')
    row = cur.fetchone()
    if row and row[0] == 'ok':
        print('Integrity check passed: OK')
        conn.close()
        raise SystemExit(0)
    else:
        print('Integrity check failed:', row)
        # try to dump
        try:
            print('Attempting to dump database to SQL...')
            dump_sql = ''.join(conn.iterdump())
            conn.close()
            # write dump to temp file
            dump_file = path.with_suffix('.dump.sql')
            with open(dump_file, 'w', encoding='utf-8') as f:
                f.write(dump_sql)
            print(f'Dump written to {dump_file}')

            # backup corrupted DB
            shutil.copy2(path, backup)
            print(f'Backed up corrupted DB to {backup}')

            # remove old DB and create new
            path.unlink()
            print('Removed corrupted DB file')

            # create new DB and load dump
            conn2 = sqlite3.connect(str(path))
            cur2 = conn2.cursor()
            with open(dump_file, 'r', encoding='utf-8') as f:
                sql = f.read()
            # execute script
            cur2.executescript(sql)
            conn2.commit()
            conn2.close()
            print('Recreated DB from dump (may be partial).')

            # run ORM migrations/init
            try:
                from app.db.database import init_db as _init_db
                _init_db()
                print('Initialized DB schema via SQLAlchemy.')
            except Exception as ie:
                print('Failed to init DB via SQLAlchemy:', repr(ie))
            raise SystemExit(0)
        except Exception as e:
            print('Dump failed:', repr(e))
            try:
                conn.close()
            except Exception:
                pass
            # fallback: backup and recreate empty DB
            shutil.copy2(path, backup)
            print(f'Backed up corrupted DB to {backup}')
            path.unlink()
            print('Removed corrupted DB file')
            try:
                from app.db.database import init_db as _init_db
                _init_db()
                print('Created fresh empty database.')
            except Exception as ie:
                print('Failed to create fresh DB via SQLAlchemy:', repr(ie))
            raise SystemExit(0)
except sqlite3.DatabaseError as e:
    print('Database error:', repr(e))
    # try to backup and recreate
    shutil.copy2(path, backup)
    print(f'Backed up corrupted DB to {backup}')
    try:
        path.unlink()
        print('Removed corrupted DB file')
    except Exception as ex:
        print('Failed to remove DB:', ex)
    try:
        from app.db.database import init_db as _init_db
        _init_db()
        print('Created fresh empty database.')
    except Exception as ie:
        print('Failed to create fresh DB via SQLAlchemy:', repr(ie))
except Exception as e:
    print('Unexpected error:', repr(e))
    raise
