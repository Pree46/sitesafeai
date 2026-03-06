"""
SiteSafeAI — Mock Data Seeder
Run this script to populate the database with realistic test data.
Usage: python -m backend.seed
"""

import random
import sqlite3
from datetime import datetime, timedelta
from backend.database import get_connection, init_db, DB_PATH
import os

# Worker names
WORKER_NAMES = [
    "Rajesh Kumar", "Anita Sharma", "Mohammed Ali", "Priya Patel",
    "Suresh Reddy", "Kavitha Nair", "Amit Singh", "Deepa Krishnan",
    "Vikram Joshi", "Lakshmi Rao", "Arjun Mehta", "Sunita Gupta",
    "Ravi Shankar", "Meena Devi", "Karthik Iyer", "Pooja Verma",
    "Sanjay Tiwari", "Rekha Pillai", "Dinesh Pandey", "Anjali Mishra"
]

ROLES = ["Worker", "Supervisor", "Electrician", "Welder", "Mason", "Crane Operator", "Foreman"]

ZONE_DATA = [
    ("Zone A - Main Building", "restricted", "high"),
    ("Zone B - Crane Area", "restricted", "high"),
    ("Zone C - Scaffolding", "warning", "medium"),
    ("Zone D - Material Storage", "warning", "medium"),
    ("Zone E - Entry Gate", "safe", "low"),
]

VIOLATION_TYPES = {
    1: ["NO-Mask"],
    2: ["NO-Safety Vest", "NO-Hardhat"],
    3: ["Restricted Zone Entry", "Multiple PPE Violations"],
}

def seed():
    """Populate the database with mock data."""
    # Delete existing DB and recreate
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    # --- Workers ---
    workers = []
    for i, name in enumerate(WORKER_NAMES):
        reg_date = (datetime.now() - timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d")
        role = random.choice(ROLES)
        is_active = 1 if random.random() > 0.15 else 0
        cursor.execute(
            "INSERT INTO workers (name, role, registration_date, is_active) VALUES (?, ?, ?, ?)",
            (name, role, reg_date, is_active)
        )
        workers.append(cursor.lastrowid)
    
    # --- Zones ---
    zones = []
    for name, zone_type, risk_level in ZONE_DATA:
        created_at = (datetime.now() - timedelta(days=random.randint(60, 180))).strftime("%Y-%m-%d")
        coords = f"[{random.randint(0,500)},{random.randint(0,400)},{random.randint(100,640)},{random.randint(100,480)}]"
        cursor.execute(
            "INSERT INTO zones (name, zone_type, risk_level, coordinates, created_at) VALUES (?, ?, ?, ?, ?)",
            (name, zone_type, risk_level, coords, created_at)
        )
        zones.append(cursor.lastrowid)

    # --- Violations (last 30 days) ---
    now = datetime.now()
    for day_offset in range(30):
        date = now - timedelta(days=day_offset)
        # More violations on weekdays, fewer on weekends
        is_weekend = date.weekday() >= 5
        num_violations = random.randint(2, 6) if is_weekend else random.randint(5, 18)

        for _ in range(num_violations):
            worker_id = random.choice(workers)
            zone_id = random.choice(zones)

            # Weighted severity: more minor, fewer critical
            grade = random.choices([1, 2, 3], weights=[45, 35, 20])[0]
            violation_type = random.choice(VIOLATION_TYPES[grade])

            hour = random.randint(7, 18)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            ts = date.replace(hour=hour, minute=minute, second=second).strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute(
                "INSERT INTO violations (worker_id, zone_id, violation_type, severity_grade, timestamp) VALUES (?, ?, ?, ?, ?)",
                (worker_id, zone_id, violation_type, grade, ts)
            )

    conn.commit()

    # Print stats
    total_v = cursor.execute("SELECT COUNT(*) FROM violations").fetchone()[0]
    total_w = cursor.execute("SELECT COUNT(*) FROM workers").fetchone()[0]
    total_z = cursor.execute("SELECT COUNT(*) FROM zones").fetchone()[0]
    conn.close()

    print(f"✅ Database seeded: {total_w} workers, {total_z} zones, {total_v} violations")
    print(f"📁 Database at: {DB_PATH}")


if __name__ == "__main__":
    seed()
