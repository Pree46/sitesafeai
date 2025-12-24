from .engine import GeofenceEngine
from .zones import load_zones
from .alerts import AlertManager

# Load zones once at startup
try:
    zones = load_zones("zones_config.json")
except Exception:
    zones = []

alert_manager = AlertManager(cooldown=15)

geofence_engine = GeofenceEngine(zones, alert_manager)
