"""
SiteSafeAI — SQLite Database Layer
Creates and manages the sitesafe.db database with workers, zones, and violations tables.
"""

import sqlite3
import os

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database")
DB_PATH = os.path.join(DB_DIR, "sitesafe.db")


def get_connection():
    """Get a database connection with row_factory for dict-like access."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS workers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT DEFAULT 'Worker',
            face_encoding TEXT,
            registration_date TEXT NOT NULL,
            is_active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS zones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            zone_type TEXT NOT NULL CHECK(zone_type IN ('restricted', 'warning', 'safe')),
            risk_level TEXT NOT NULL CHECK(risk_level IN ('high', 'medium', 'low')),
            coordinates TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id INTEGER NOT NULL,
            zone_id INTEGER,
            violation_type TEXT NOT NULL,
            severity_grade INTEGER NOT NULL CHECK(severity_grade IN (1, 2, 3)),
            timestamp TEXT NOT NULL,
            image_evidence TEXT,
            FOREIGN KEY (worker_id) REFERENCES workers(id),
            FOREIGN KEY (zone_id) REFERENCES zones(id)
        );

        CREATE INDEX IF NOT EXISTS idx_violations_timestamp ON violations(timestamp);
        CREATE INDEX IF NOT EXISTS idx_violations_worker ON violations(worker_id);
        CREATE INDEX IF NOT EXISTS idx_violations_zone ON violations(zone_id);
        CREATE INDEX IF NOT EXISTS idx_violations_severity ON violations(severity_grade);
    """)

    conn.commit()
    conn.close()


# Auto-initialize on import
init_db()
