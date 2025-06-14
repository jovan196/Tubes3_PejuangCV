# dump_db.py
# Script to dump the entire SQLite database (ats.db) into an SQL file

import os
import sqlite3

# Determine paths
WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DB_PATH = os.path.join(WORKSPACE, 'ats.db')
DUMP_FILE = os.path.join(WORKSPACE, 'data', 'seed_data.sql')

# Ensure the database exists
if not os.path.exists(DB_PATH):
    print(f"Database file not found: {DB_PATH}")
    exit(1)

# Connect and dump
conn = sqlite3.connect(DB_PATH)
try:
    with open(DUMP_FILE, 'w', encoding='utf-8') as f:
        for line in conn.iterdump():
            f.write(f"{line}\n")
    print(f"Database dumped successfully to {DUMP_FILE}")
finally:
    conn.close()
