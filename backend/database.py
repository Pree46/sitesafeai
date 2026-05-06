"""
SiteSafeAI — SQLite Database Layer
Creates and manages the sitesafe.db database with workers, zones, and violations tables.
"""

import sqlite3
import os

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database")
DB_PATH = os.path.join(DB_DIR, "sitesafe.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS violations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        worker_id TEXT,
        violation_type TEXT,
        severity_grade INTEGER,
        zone_name TEXT,
        is_geofence INTEGER DEFAULT 0,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()