from backend.database import get_connection

conn = get_connection()
cursor = conn.cursor()

rows = cursor.execute("""
SELECT zone_name, is_geofence, violation_type
FROM violations
ORDER BY id DESC
LIMIT 20
""").fetchall()

for r in rows:
    print(dict(r))

conn.close()