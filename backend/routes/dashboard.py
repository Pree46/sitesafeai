"""
SiteSafeAI — Dashboard API Routes
All analytics, metrics, and data endpoints for the dashboard frontend.
"""

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from typing import Optional
from datetime import datetime, timedelta
from backend.database import get_connection
import csv
import io

router = APIRouter(prefix="/api")


# ──────────────────────────────────────────────
#  METRICS OVERVIEW
# ──────────────────────────────────────────────

@router.get("/metrics/overview")
def metrics_overview():
    conn = get_connection()
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    total_workers = conn.execute("SELECT COUNT(*) FROM workers").fetchone()[0]
    active_workers = conn.execute("SELECT COUNT(*) FROM workers WHERE is_active = 1").fetchone()[0]

    violations_today = conn.execute(
        "SELECT COUNT(*) FROM violations WHERE DATE(timestamp) = ?", (today,)
    ).fetchone()[0]

    high_severity_today = conn.execute(
        "SELECT COUNT(*) FROM violations WHERE DATE(timestamp) = ? AND severity_grade = 3", (today,)
    ).fetchone()[0]

    total_zones = conn.execute("SELECT COUNT(*) FROM zones").fetchone()[0]

    # PPE compliance: (active workers - workers with violations today) / active workers * 100
    workers_with_violations = conn.execute(
        "SELECT COUNT(DISTINCT worker_id) FROM violations WHERE DATE(timestamp) = ?", (today,)
    ).fetchone()[0]

    ppe_compliance = round(
        ((active_workers - workers_with_violations) / max(active_workers, 1)) * 100, 1
    )

    violations_yesterday = conn.execute(
        "SELECT COUNT(*) FROM violations WHERE DATE(timestamp) = ?", (yesterday,)
    ).fetchone()[0]

    conn.close()

    return {
        "total_workers": total_workers,
        "active_workers": active_workers,
        "violations_today": violations_today,
        "high_severity_today": high_severity_today,
        "total_zones": total_zones,
        "ppe_compliance_rate": ppe_compliance,
        "violations_yesterday": violations_yesterday,
    }


# ──────────────────────────────────────────────
#  WORKERS
# ──────────────────────────────────────────────

@router.get("/workers")
def get_workers(search: Optional[str] = None):
    conn = get_connection()

    query = """
        SELECT w.id, w.name, w.role, w.registration_date, w.is_active,
               COUNT(v.id) as violation_count,
               MAX(v.timestamp) as last_seen
        FROM workers w
        LEFT JOIN violations v ON w.id = v.worker_id
    """
    params = []
    if search:
        query += " WHERE w.name LIKE ?"
        params.append(f"%{search}%")
    query += " GROUP BY w.id ORDER BY violation_count DESC"

    rows = conn.execute(query, params).fetchall()

    workers = []
    for r in rows:
        # Get most common violation for this worker
        most_common = conn.execute(
            "SELECT violation_type, COUNT(*) as cnt FROM violations WHERE worker_id = ? GROUP BY violation_type ORDER BY cnt DESC LIMIT 1",
            (r["id"],)
        ).fetchone()

        workers.append({
            "id": r["id"],
            "name": r["name"],
            "role": r["role"],
            "registration_date": r["registration_date"],
            "is_active": r["is_active"],
            "violation_count": r["violation_count"],
            "most_common_violation": most_common["violation_type"] if most_common else None,
            "last_seen": r["last_seen"],
        })

    conn.close()
    return workers


@router.get("/workers/top-violators")
def top_violators():
    conn = get_connection()
    rows = conn.execute("""
        SELECT w.id, w.name, w.role, COUNT(v.id) as violation_count
        FROM workers w
        JOIN violations v ON w.id = v.worker_id
        GROUP BY w.id
        ORDER BY violation_count DESC
        LIMIT 5
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ──────────────────────────────────────────────
#  VIOLATIONS
# ──────────────────────────────────────────────

@router.get("/violations")
def get_violations(
    date: Optional[str] = None,
    zone_id: Optional[int] = None,
    severity: Optional[int] = None,
    limit: int = Query(default=100, le=500),
):
    conn = get_connection()
    query = """
        SELECT v.*, w.name as worker_name, z.name as zone_name
        FROM violations v
        LEFT JOIN workers w ON v.worker_id = w.id
        LEFT JOIN zones z ON v.zone_id = z.id
        WHERE 1=1
    """
    params = []

    if date:
        query += " AND DATE(v.timestamp) = ?"
        params.append(date)
    if zone_id:
        query += " AND v.zone_id = ?"
        params.append(zone_id)
    if severity:
        query += " AND v.severity_grade = ?"
        params.append(severity)

    query += " ORDER BY v.timestamp DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/violations/today")
def violations_today():
    conn = get_connection()
    today = datetime.now().strftime("%Y-%m-%d")
    rows = conn.execute("""
        SELECT v.*, w.name as worker_name, z.name as zone_name
        FROM violations v
        LEFT JOIN workers w ON v.worker_id = w.id
        LEFT JOIN zones z ON v.zone_id = z.id
        WHERE DATE(v.timestamp) = ?
        ORDER BY v.timestamp DESC
    """, (today,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/violations/feed")
def violation_feed():
    """Last 20 violations for real-time feed."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT v.id, v.violation_type, v.severity_grade, v.timestamp,
               w.name as worker_name, z.name as zone_name
        FROM violations v
        LEFT JOIN workers w ON v.worker_id = w.id
        LEFT JOIN zones z ON v.zone_id = z.id
        ORDER BY v.timestamp DESC
        LIMIT 20
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ──────────────────────────────────────────────
#  ANALYTICS
# ──────────────────────────────────────────────

@router.get("/analytics/severity")
def severity_distribution():
    conn = get_connection()
    rows = conn.execute("""
        SELECT severity_grade, COUNT(*) as count
        FROM violations
        GROUP BY severity_grade
        ORDER BY severity_grade
    """).fetchall()
    conn.close()

    labels = {1: "Minor", 2: "Medium", 3: "Critical"}
    colors = {1: "#22c55e", 2: "#eab308", 3: "#ef4444"}

    return [
        {
            "grade": r["severity_grade"],
            "label": labels.get(r["severity_grade"], "Unknown"),
            "count": r["count"],
            "color": colors.get(r["severity_grade"], "#888"),
        }
        for r in rows
    ]


@router.get("/analytics/zone")
def zone_analytics():
    conn = get_connection()
    today = datetime.now().strftime("%Y-%m-%d")

    rows = conn.execute("""
        SELECT z.id, z.name, z.zone_type, z.risk_level,
               COUNT(CASE WHEN DATE(v.timestamp) = ? THEN 1 END) as violations_today,
               COUNT(v.id) as violations_total
        FROM zones z
        LEFT JOIN violations v ON z.id = v.zone_id
        GROUP BY z.id
        ORDER BY violations_total DESC
    """, (today,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/analytics/daily")
def daily_violations(days: int = Query(default=14, le=90)):
    conn = get_connection()
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    rows = conn.execute("""
        SELECT DATE(timestamp) as date,
               SUM(CASE WHEN severity_grade = 1 THEN 1 ELSE 0 END) as grade_1,
               SUM(CASE WHEN severity_grade = 2 THEN 1 ELSE 0 END) as grade_2,
               SUM(CASE WHEN severity_grade = 3 THEN 1 ELSE 0 END) as grade_3,
               COUNT(*) as total
        FROM violations
        WHERE DATE(timestamp) >= ?
        GROUP BY DATE(timestamp)
        ORDER BY date
    """, (start_date,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/analytics/calendar")
def calendar_heatmap(days: int = Query(default=90, le=365)):
    conn = get_connection()
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    rows = conn.execute("""
        SELECT DATE(timestamp) as date, COUNT(*) as count
        FROM violations
        WHERE DATE(timestamp) >= ?
        GROUP BY DATE(timestamp)
        ORDER BY date
    """, (start_date,)).fetchall()
    conn.close()

    if not rows:
        return []

    max_count = max(r["count"] for r in rows)

    return [
        {
            "date": r["date"],
            "count": r["count"],
            "level": min(4, int((r["count"] / max(max_count, 1)) * 4) + (1 if r["count"] > 0 else 0)),
        }
        for r in rows
    ]


@router.get("/analytics/safety-score")
def safety_score():
    conn = get_connection()
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    # Weighted violation score for today
    row = conn.execute("""
        SELECT
            SUM(CASE WHEN severity_grade = 1 THEN 1 ELSE 0 END) as g1,
            SUM(CASE WHEN severity_grade = 2 THEN 1 ELSE 0 END) as g2,
            SUM(CASE WHEN severity_grade = 3 THEN 1 ELSE 0 END) as g3
        FROM violations WHERE DATE(timestamp) = ?
    """, (today,)).fetchone()

    g1, g2, g3 = row["g1"] or 0, row["g2"] or 0, row["g3"] or 0
    weighted_score = (g1 * 1) + (g2 * 3) + (g3 * 5)
    score = max(0, round(100 - weighted_score, 1))

    # Yesterday's score for trend
    row_y = conn.execute("""
        SELECT
            SUM(CASE WHEN severity_grade = 1 THEN 1 ELSE 0 END) as g1,
            SUM(CASE WHEN severity_grade = 2 THEN 1 ELSE 0 END) as g2,
            SUM(CASE WHEN severity_grade = 3 THEN 1 ELSE 0 END) as g3
        FROM violations WHERE DATE(timestamp) = ?
    """, (yesterday,)).fetchone()

    g1y, g2y, g3y = row_y["g1"] or 0, row_y["g2"] or 0, row_y["g3"] or 0
    score_y = max(0, round(100 - ((g1y * 1) + (g2y * 3) + (g3y * 5)), 1))

    if score > score_y:
        trend = "up"
    elif score < score_y:
        trend = "down"
    else:
        trend = "stable"

    # Letter grade
    if score >= 90: grade = "A"
    elif score >= 80: grade = "B"
    elif score >= 70: grade = "C"
    elif score >= 60: grade = "D"
    else: grade = "F"

    conn.close()

    return {
        "score": score,
        "grade": grade,
        "trend": trend,
        "details": {
            "minor_violations": g1,
            "medium_violations": g2,
            "critical_violations": g3,
            "weighted_total": weighted_score,
        }
    }


@router.get("/analytics/insights")
def smart_insights():
    conn = get_connection()
    today = datetime.now().strftime("%Y-%m-%d")
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    # Most common violation today
    most_common = conn.execute("""
        SELECT violation_type, COUNT(*) as cnt
        FROM violations WHERE DATE(timestamp) = ?
        GROUP BY violation_type ORDER BY cnt DESC LIMIT 1
    """, (today,)).fetchone()

    # Most dangerous zone
    dangerous_zone = conn.execute("""
        SELECT z.name, COUNT(v.id) as cnt
        FROM violations v JOIN zones z ON v.zone_id = z.id
        WHERE DATE(v.timestamp) = ?
        GROUP BY z.id ORDER BY cnt DESC LIMIT 1
    """, (today,)).fetchone()

    # Worker with most violations
    top_worker = conn.execute("""
        SELECT w.name, COUNT(v.id) as cnt
        FROM violations v JOIN workers w ON v.worker_id = w.id
        WHERE DATE(v.timestamp) = ?
        GROUP BY w.id ORDER BY cnt DESC LIMIT 1
    """, (today,)).fetchone()

    # PPE compliance rate
    active = conn.execute("SELECT COUNT(*) FROM workers WHERE is_active = 1").fetchone()[0]
    violators = conn.execute(
        "SELECT COUNT(DISTINCT worker_id) FROM violations WHERE DATE(timestamp) = ?", (today,)
    ).fetchone()[0]
    compliance = round(((active - violators) / max(active, 1)) * 100, 1)

    # Weekly trend
    this_week = conn.execute(
        "SELECT COUNT(*) FROM violations WHERE DATE(timestamp) >= ?", (week_ago,)
    ).fetchone()[0]
    prev_week_start = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")
    prev_week = conn.execute(
        "SELECT COUNT(*) FROM violations WHERE DATE(timestamp) >= ? AND DATE(timestamp) < ?",
        (prev_week_start, week_ago)
    ).fetchone()[0]

    if prev_week > 0:
        trend_pct = round(((this_week - prev_week) / prev_week) * 100, 1)
        trend_str = f"{'↑' if trend_pct > 0 else '↓'} {abs(trend_pct)}% vs last week"
    else:
        trend_str = "No previous week data"

    conn.close()

    insights = [
        {
            "title": "Most Common Violation",
            "value": most_common["violation_type"] if most_common else "None today",
            "icon": "AlertTriangle",
            "color": "#eab308",
        },
        {
            "title": "Most Dangerous Zone",
            "value": f"{dangerous_zone['name']} ({dangerous_zone['cnt']} violations)" if dangerous_zone else "All zones safe",
            "icon": "MapPin",
            "color": "#ef4444",
        },
        {
            "title": "Highest Risk Worker",
            "value": f"{top_worker['name']} ({top_worker['cnt']} violations)" if top_worker else "No violations",
            "icon": "User",
            "color": "#f97316",
        },
        {
            "title": "PPE Compliance Rate",
            "value": f"{compliance}%",
            "icon": "Shield",
            "color": "#22c55e" if compliance >= 80 else "#eab308" if compliance >= 60 else "#ef4444",
        },
        {
            "title": "Weekly Safety Trend",
            "value": trend_str,
            "icon": "TrendingUp",
            "color": "#8b5cf6",
        },
    ]

    return insights


# ──────────────────────────────────────────────
#  ZONES
# ──────────────────────────────────────────────

@router.get("/zones")
def get_zones():
    conn = get_connection()
    today = datetime.now().strftime("%Y-%m-%d")
    rows = conn.execute("""
        SELECT z.*,
               COUNT(CASE WHEN DATE(v.timestamp) = ? THEN 1 END) as violations_today
        FROM zones z
        LEFT JOIN violations v ON z.id = v.zone_id
        GROUP BY z.id
        ORDER BY violations_today DESC
    """, (today,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ──────────────────────────────────────────────
#  EXPORT
# ──────────────────────────────────────────────

@router.get("/export/csv")
def export_csv():
    conn = get_connection()
    rows = conn.execute("""
        SELECT v.id, w.name as worker_name, z.name as zone_name,
               v.violation_type, v.severity_grade, v.timestamp
        FROM violations v
        LEFT JOIN workers w ON v.worker_id = w.id
        LEFT JOIN zones z ON v.zone_id = z.id
        ORDER BY v.timestamp DESC
    """).fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Worker", "Zone", "Violation Type", "Severity Grade", "Timestamp"])
    for r in rows:
        writer.writerow([r["id"], r["worker_name"], r["zone_name"],
                         r["violation_type"], r["severity_grade"], r["timestamp"]])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=sitesafe_violations_{datetime.now().strftime('%Y%m%d')}.csv"}
    )
