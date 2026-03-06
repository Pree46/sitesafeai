"""
SiteSafeAI — Pydantic Models for API serialization
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Worker(BaseModel):
    id: int
    name: str
    role: str = "Worker"
    registration_date: str
    is_active: int = 1
    violation_count: Optional[int] = 0
    most_common_violation: Optional[str] = None
    last_seen: Optional[str] = None


class Zone(BaseModel):
    id: int
    name: str
    zone_type: str
    risk_level: str
    coordinates: Optional[str] = None
    created_at: str
    violations_today: Optional[int] = 0


class Violation(BaseModel):
    id: int
    worker_id: int
    worker_name: Optional[str] = None
    zone_id: Optional[int] = None
    zone_name: Optional[str] = None
    violation_type: str
    severity_grade: int
    timestamp: str
    image_evidence: Optional[str] = None


class MetricsOverview(BaseModel):
    total_workers: int
    active_workers: int
    violations_today: int
    high_severity_today: int
    total_zones: int
    ppe_compliance_rate: float
    violations_yesterday: int = 0
    active_workers_yesterday: int = 0


class SeverityDistribution(BaseModel):
    grade: int
    label: str
    count: int
    color: str


class ZoneAnalytics(BaseModel):
    zone_id: int
    zone_name: str
    zone_type: str
    risk_level: str
    violations_today: int
    violations_total: int


class DailyViolation(BaseModel):
    date: str
    grade_1: int
    grade_2: int
    grade_3: int
    total: int


class CalendarEntry(BaseModel):
    date: str
    count: int
    level: int  # 0-4 intensity


class SafetyScore(BaseModel):
    score: float
    grade: str  # A, B, C, D, F
    trend: str  # up, down, stable
    details: dict


class Insight(BaseModel):
    title: str
    value: str
    icon: str
    color: str
