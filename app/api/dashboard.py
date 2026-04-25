from fastapi import APIRouter, Response
from typing import Optional
from datetime import datetime, timedelta
import random

router = APIRouter()

@router.get("/api/metrics/overview")
def get_metrics_overview():
    return {
        "total_workers": 142,
        "violations_today": 12,
        "violations_yesterday": 15,
        "total_zones": 4,
        "high_severity_today": 3,
        "ppe_compliance_rate": 92.5
    }

@router.get("/api/workers")
def get_workers(search: Optional[str] = None):
    workers = [
        {"id": "W-101", "name": "John Doe", "role": "Crane Operator", "status": "Active", "violations": 2, "last_seen": "10 mins ago"},
        {"id": "W-102", "name": "Jane Smith", "role": "Site Engineer", "status": "Active", "violations": 0, "last_seen": "2 mins ago"},
        {"id": "W-103", "name": "Mike Johnson", "role": "Welder", "status": "Offline", "violations": 5, "last_seen": "2 hours ago"},
        {"id": "W-104", "name": "Alice Brown", "role": "Electrician", "status": "Active", "violations": 1, "last_seen": "1 min ago"},
    ]
    if search:
        search = search.lower()
        workers = [w for w in workers if search in w["name"].lower() or search in w["id"].lower()]
    return workers

@router.get("/api/workers/top-violators")
def get_top_violators():
    return [
        {"name": "Mike Johnson", "id": "W-103", "count": 5},
        {"name": "Tom Wilson", "id": "W-108", "count": 4},
        {"name": "Sarah Davis", "id": "W-112", "count": 3},
        {"name": "John Doe", "id": "W-101", "count": 2},
    ]

@router.get("/api/violations")
def get_violations():
    return []

@router.get("/api/violations/today")
def get_violations_today():
    return {"count": 12}

@router.get("/api/violations/feed")
def get_violation_feed():
    now = datetime.now()
    return [
        {
            "id": "V-1001",
            "type": "No Hardhat",
            "severity": "high",
            "worker": "Mike Johnson",
            "zone": "Zone A",
            "time": (now - timedelta(minutes=5)).strftime("%I:%M %p"),
            "image": None
        },
        {
            "id": "V-1002",
            "type": "No Vest",
            "severity": "medium",
            "worker": "John Doe",
            "zone": "Zone C",
            "time": (now - timedelta(minutes=25)).strftime("%I:%M %p"),
            "image": None
        },
        {
            "id": "V-1003",
            "type": "Unauthorized Entry",
            "severity": "high",
            "worker": "Unknown",
            "zone": "Restricted Area B",
            "time": (now - timedelta(hours=1)).strftime("%I:%M %p"),
            "image": None
        }
    ]

@router.get("/api/analytics/severity")
def get_severity_dist():
    return [
        {"name": "High", "value": 15, "color": "#ef4444"},
        {"name": "Medium", "value": 35, "color": "#f59e0b"},
        {"name": "Low", "value": 50, "color": "#3b82f6"}
    ]

@router.get("/api/analytics/zone")
def get_zone_analytics():
    return [
        {"zone": "Zone A", "violations": 45},
        {"zone": "Zone B", "violations": 20},
        {"zone": "Zone C", "violations": 35},
        {"zone": "Zone D", "violations": 10}
    ]

@router.get("/api/analytics/daily")
def get_daily_violations(days: int = 14):
    data = []
    base_date = datetime.now()
    for i in range(days):
        date_str = (base_date - timedelta(days=days-1-i)).strftime("%b %d")
        data.append({
            "date": date_str,
            "total": random.randint(5, 25),
            "high_severity": random.randint(0, 5)
        })
    return data

@router.get("/api/analytics/calendar")
def get_calendar(days: int = 90):
    data = []
    base_date = datetime.now()
    for i in range(days):
        date_str = (base_date - timedelta(days=days-1-i)).strftime("%Y-%m-%d")
        data.append({
            "date": date_str,
            "count": random.randint(0, 30)
        })
    return data

@router.get("/api/analytics/safety-score")
def get_safety_score():
    return {
        "score": 88,
        "grade": "B+",
        "trend": "up"
    }

@router.get("/api/analytics/insights")
def get_insights():
    return [
        {
            "type": "warning",
            "title": "High Risk in Zone A",
            "description": "Violation frequency increased by 40% in the last 48 hours."
        },
        {
            "type": "success",
            "title": "PPE Compliance Up",
            "description": "Overall hardhat compliance improved to 95% this week."
        },
        {
            "type": "info",
            "title": "Shift Handover Issue",
            "description": "Most violations occur between 2:00 PM and 3:00 PM."
        }
    ]

@router.get("/api/zones")
def get_dashboard_zones():
    return [
        {"id": "Z-01", "name": "Zone A", "riskLevel": "High", "activeWorkers": 12, "status": "Active"},
        {"id": "Z-02", "name": "Zone B", "riskLevel": "Medium", "activeWorkers": 8, "status": "Active"},
        {"id": "Z-03", "name": "Zone C", "riskLevel": "Low", "activeWorkers": 25, "status": "Active"},
        {"id": "Z-04", "name": "Restricted Area", "riskLevel": "Critical", "activeWorkers": 0, "status": "Locked"}
    ]

@router.get("/api/export/csv")
def export_csv():
    # Return dummy CSV
    csv_content = "date,zone,worker,type,severity\n2023-10-01,Zone A,W-101,No Hardhat,High\n"
    return Response(content=csv_content, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=report.csv"})
