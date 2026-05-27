import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'kudos.db')
MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), 'migrations')

def ensure_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def applied(conn):
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM migrations")
        rows = [r[0] for r in cur.fetchall()]
        return set(rows)
    except Exception:
        return set()

def apply_migration(conn, path, mid):
    with open(path, 'r', encoding='utf-8') as f:
        sql = f.read()
    cur = conn.cursor()
    cur.executescript(sql)
    cur.execute('INSERT OR REPLACE INTO migrations (id) VALUES (?)', (mid,))
    conn.commit()
    print('applied', mid)

if __name__ == '__main__':
    conn = ensure_db()
    existing = applied(conn)
    files = sorted([f for f in os.listdir(MIGRATIONS_DIR) if f.endswith('.sql')])
    for fn in files:
        mid = fn
        if mid in existing:
            print('skip', mid)
            continue
        apply_migration(conn, os.path.join(MIGRATIONS_DIR, fn), mid)
    print('migrations complete')
