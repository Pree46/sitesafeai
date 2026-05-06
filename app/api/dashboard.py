from fastapi import APIRouter, Response
from datetime import datetime
from backend.database import get_connection

router = APIRouter()


# =========================================================
# KPI METRICS
# =========================================================
@router.get("/api/metrics/overview")
def metrics():

    conn = get_connection()
    cursor = conn.cursor()

    total_violations = cursor.execute("""
    SELECT COUNT(*) FROM violations
    WHERE is_geofence = 0
    """).fetchone()[0]

    restricted_zones = cursor.execute("""
    SELECT COUNT(DISTINCT zone_name)
    FROM violations
    WHERE is_geofence = 1
    """).fetchone()[0]

    high_risk = cursor.execute("""
    SELECT COUNT(*) FROM violations
    WHERE is_geofence = 1
    """).fetchone()[0]

    active_workers = cursor.execute("""
    SELECT COUNT(DISTINCT worker_id)
    FROM violations
    """).fetchone()[0]

    conn.close()

    compliance = max(0, 100 - int(total_violations * 0.5))

    return {
        "total_workers": active_workers,
        "violations_today": total_violations,
        "total_zones": restricted_zones,
        "high_severity_today": high_risk,
        "ppe_compliance_rate": compliance
    }


# =========================================================
# WORKER INTELLIGENCE
# =========================================================
@router.get("/api/workers")
def worker_intelligence():

    conn = get_connection()
    cursor = conn.cursor()

    rows = cursor.execute("""
    SELECT
        worker_id,
        COUNT(*) as total,
        MAX(timestamp) as latest
    FROM violations
    GROUP BY worker_id
    ORDER BY total DESC
    """).fetchall()

    result = []

    for r in rows:

        common = cursor.execute("""
        SELECT violation_type
        FROM violations
        WHERE worker_id = ?
        GROUP BY violation_type
        ORDER BY COUNT(*) DESC
        LIMIT 1
        """, (r["worker_id"],)).fetchone()

        result.append({
            "id": r["worker_id"],
            "name": r["worker_id"],
            "violations": r["total"],
            "most_common": common[0] if common else "-",
            "status": "ACTIVE"
        })

    conn.close()

    return result


# =========================================================
# TOP VIOLATORS
# =========================================================
@router.get("/api/workers/top-violators")
def top_violators():

    conn = get_connection()
    cursor = conn.cursor()

    rows = cursor.execute("""
    SELECT
        worker_id,
        COUNT(*) as total
    FROM violations
    GROUP BY worker_id
    ORDER BY total DESC
    LIMIT 5
    """).fetchall()

    conn.close()

    return [
        {
            "worker_id": r["worker_id"] or "Unknown",
            "violations": r["total"]
        }
        for r in rows
    ]


# =========================================================
# LIVE FEED
# =========================================================
@router.get("/api/violations/feed")
def live_feed():

    conn = get_connection()
    cursor = conn.cursor()

    rows = cursor.execute("""
    SELECT *
    FROM violations
    ORDER BY id DESC
    LIMIT 20
    """).fetchall()

    conn.close()

    return [
        {
            "id": r["id"],
            "worker_id": r["worker_id"] or "Unknown",
            "type": r["violation_type"],
            "zone": r["zone_name"],
            "severity": r["severity_grade"],
            "time": r["timestamp"]
        }
        for r in rows
    ]


# =========================================================
# SEVERITY DISTRIBUTION
# =========================================================
@router.get("/api/analytics/severity")
def severity_distribution():

    conn = get_connection()
    cursor = conn.cursor()

    rows = cursor.execute("""
    SELECT severity_grade, COUNT(*) as total
    FROM violations
    GROUP BY severity_grade
    """).fetchall()

    conn.close()

    result = {
        1: 0,
        2: 0,
        3: 0
    }

    for r in rows:
        result[r["severity_grade"]] = r["total"]

    return [
        {
            "name": "Critical",
            "value": result[3],
            "color": "#ef4444"
        },
        {
            "name": "Medium",
            "value": result[2],
            "color": "#f59e0b"
        },
        {
            "name": "Minor",
            "value": result[1],
            "color": "#22c55e"
        }
    ]


# =========================================================
# ZONE VIOLATIONS
# =========================================================
@router.get("/api/analytics/zone")
def zone_violations():

    conn = get_connection()
    cursor = conn.cursor()

    rows = cursor.execute("""
    SELECT
        zone_name,
        COUNT(*) as total
    FROM violations
    WHERE is_geofence = 1
    GROUP BY zone_name
    ORDER BY total DESC
    """).fetchall()

    conn.close()

    return [
        {
            "name": r["zone_name"],
            "value": r["total"]
        }
        for r in rows
    ]


# =========================================================
# DAILY TREND
# =========================================================
@router.get("/api/analytics/daily")
def daily_trend():

    conn = get_connection()
    cursor = conn.cursor()

    rows = cursor.execute("""
    SELECT
        strftime('%H', timestamp) as hour,

        SUM(
            CASE
                WHEN severity_grade = 3 THEN 1
                ELSE 0
            END
        ) as critical,

        SUM(
            CASE
                WHEN severity_grade = 2 THEN 1
                ELSE 0
            END
        ) as medium,

        SUM(
            CASE
                WHEN severity_grade = 1 THEN 1
                ELSE 0
            END
        ) as minor

    FROM violations
    GROUP BY hour
    ORDER BY hour
    """).fetchall()

    conn.close()

    return [
        {
            "name": f"{r['hour']}:00",
            "Critical": r["critical"] or 0,
            "Medium": r["medium"] or 0,
            "Minor": r["minor"] or 0
        }
        for r in rows
    ]


# =========================================================
# SAFETY SCORE
# =========================================================
@router.get("/api/analytics/safety-score")
def get_safety_score():

    conn = get_connection()
    cursor = conn.cursor()

    total = cursor.execute("""
    SELECT COUNT(*) FROM violations
    """).fetchone()[0]

    conn.close()

    score = max(0, 100 - int(total * 0.5))

    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B+"
    elif score >= 70:
        grade = "B"
    else:
        grade = "C"

    return {
        "score": score,
        "grade": grade,
        "trend": "up" if score > 70 else "down"
    }


# =========================================================
# AI INSIGHTS
# =========================================================
@router.get("/api/analytics/insights")
def insights():

    conn = get_connection()
    cursor = conn.cursor()

    common_violation = cursor.execute("""
    SELECT violation_type, COUNT(*) as total
    FROM violations
    GROUP BY violation_type
    ORDER BY total DESC
    LIMIT 1
    """).fetchone()

    high_zone = cursor.execute("""
    SELECT zone_name, COUNT(*) as total
    FROM violations
    WHERE is_geofence = 1
    GROUP BY zone_name
    ORDER BY total DESC
    LIMIT 1
    """).fetchone()

    conn.close()

    return [
        {
            "title": "Most Common Violation",
            "value": common_violation[0] if common_violation else "None"
        },
        {
            "title": "Highest Risk Zone",
            "value": high_zone[0] if high_zone else "No Zone"
        }
    ]


# =========================================================
# ZONE INTELLIGENCE
# =========================================================
@router.get("/api/zones")
def get_dashboard_zones():

    conn = get_connection()
    cursor = conn.cursor()

    rows = cursor.execute("""
    SELECT
        zone_name,
        COUNT(*) as total
    FROM violations
    WHERE is_geofence = 1
    GROUP BY zone_name
    ORDER BY total DESC
    """).fetchall()

    conn.close()

    return [
        {
            "name": r["zone_name"],
            "violations": r["total"],
            "status": "ACTIVE"
        }
        for r in rows
    ]


# =========================================================
# EXPORT CSV
# =========================================================
@router.get("/api/export/csv")
def export_csv():

    conn = get_connection()
    cursor = conn.cursor()

    rows = cursor.execute("""
    SELECT *
    FROM violations
    ORDER BY id DESC
    """).fetchall()

    conn.close()

    csv_content = "worker_id,type,zone,severity,time\n"

    for r in rows:
        csv_content += (
            f"{r['worker_id']},"
            f"{r['violation_type']},"
            f"{r['zone_name']},"
            f"{r['severity_grade']},"
            f"{r['timestamp']}\n"
        )

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=sitesafe_report.csv"
        }
    )