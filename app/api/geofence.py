"""
Geofence API Routes
Add this as a new file: app/api/geofence.py
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import json
import os

from ..services.alerts import state

router = APIRouter()


class ZoneCreate(BaseModel):
    name: str
    points: List[List[float]]  # [[x1,y1], [x2,y2], ...]
    color: List[int] = [255, 0, 0]  # RGB
    alpha: float = 0.3


@router.post("/api/geofence/enable")
def enable_geofence():
    """Enable geofence detection"""
    state["geofence_enabled"] = True
    return {"status": "geofence enabled"}


@router.post("/api/geofence/disable")
def disable_geofence():
    """Disable geofence detection"""
    state["geofence_enabled"] = False
    return {"status": "geofence disabled"}


@router.get("/api/geofence/status")
def get_geofence_status():
    """Check if geofencing is active"""
    return {
        "enabled": state.get("geofence_enabled", False),
        "zones_count": len(state.get("zones", []))
    }


@router.post("/api/geofence/zones")
def save_zone(zone: ZoneCreate):
    """Save a new geofence zone"""
    if "zones" not in state:
        state["zones"] = []
    
    zone_data = {
        "name": zone.name,
        "points": zone.points,
        "color": zone.color,
        "alpha": zone.alpha
    }
    
    state["zones"].append(zone_data)
    
    # Save to file for persistence
    zones_file = "zones.json"
    try:
        with open(zones_file, "w") as f:
            json.dump(state["zones"], f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save zones to file: {e}")
    
    return {
        "status": "zone saved",
        "zone": zone_data,
        "total_zones": len(state["zones"])
    }


@router.get("/api/geofence/zones")
def get_zones():
    """Get all saved zones"""
    zones_file = "zones.json"
    
    # Try to load from file first
    if os.path.exists(zones_file):
        try:
            with open(zones_file, "r") as f:
                state["zones"] = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load zones: {e}")
            state["zones"] = []
    else:
        state["zones"] = []
    
    return {
        "zones": state.get("zones", []),
        "count": len(state.get("zones", []))
    }


@router.delete("/api/geofence/zones/{zone_name}")
def delete_zone(zone_name: str):
    """Delete a specific zone"""
    zones = state.get("zones", [])
    state["zones"] = [z for z in zones if z["name"] != zone_name]
    
    # Update file
    zones_file = "zones.json"
    try:
        with open(zones_file, "w") as f:
            json.dump(state["zones"], f, indent=2)
    except Exception as e:
        print(f"Warning: Could not update zones file: {e}")
    
    return {
        "status": "zone deleted",
        "zone_name": zone_name,
        "remaining_zones": len(state["zones"])
    }


@router.delete("/api/geofence/zones")
def clear_all_zones():
    """Clear all zones"""
    state["zones"] = []
    
    zones_file = "zones.json"
    try:
        with open(zones_file, "w") as f:
            json.dump([], f)
    except Exception as e:
        print(f"Warning: Could not clear zones file: {e}")
    
    return {"status": "all zones cleared"}