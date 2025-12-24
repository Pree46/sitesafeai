import time

# Alert cooldown (seconds)
ALERT_COOLDOWN_SECONDS = 15


class AlertManager:
    """Manages alert cooldowns for PPE and geofence violations"""
    
    def __init__(self, cooldown=ALERT_COOLDOWN_SECONDS):
        self.cooldown = cooldown
        self.last_alert = 0
        self.last_geofence_alert = {}  # Track per zone

    def can_alert(self):
        """Check if PPE alert can be triggered"""
        return time.time() - self.last_alert > self.cooldown

    def can_alert_geofence(self, zone_name):
        """Check if geofence alert can be triggered for specific zone"""
        last = self.last_geofence_alert.get(zone_name, 0)
        return time.time() - last > self.cooldown

    def trigger(self, message):
        """Trigger a PPE violation alert"""
        self.last_alert = time.time()
        return {
            "message": message,
            "timestamp": time.strftime("%H:%M:%S"),
            "type": "ppe"
        }

    def trigger_geofence(self, zone_name, object_class):
        """Trigger a geofence violation alert"""
        self.last_geofence_alert[zone_name] = time.time()
        return {
            "message": f"Zone violation: {object_class} entered '{zone_name}'",
            "timestamp": time.strftime("%H:%M:%S"),
            "type": "geofence",
            "zone": zone_name,
            "object": object_class
        }


# Global alert manager instance
alert_manager = AlertManager()

# Shared state for stream control and zones
state = {
    "streaming_active": False,
    "geofence_enabled": False,
    "zones": [],
    "last_alert_time": 0  # Backward compatibility
}