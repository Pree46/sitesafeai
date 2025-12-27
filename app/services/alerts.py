import time

# Alert cooldown (seconds)
ALERT_COOLDOWN_SECONDS = 15


class AlertManager:
    """Manages alert cooldowns for PPE and geofence violations"""

    def __init__(self, cooldown=ALERT_COOLDOWN_SECONDS):
        self.cooldown = cooldown
        self.last_alert = 0
        self.last_geofence_alert = {}

    def can_alert(self):
        return time.time() - self.last_alert > self.cooldown

    def can_alert_geofence(self, zone_name):
        last = self.last_geofence_alert.get(zone_name, 0)
        return time.time() - last > self.cooldown

    def trigger(self, message):
        """
        PPE alert.
        Message MUST already contain worker id.
        """
        self.last_alert = time.time()

        return {
            "type": "PPE",
            "message": message,
            "text": message,
            "description": message,
            "timestamp": time.strftime("%H:%M:%S"),
        }

    def trigger_geofence(self, zone_name, object_class):
        self.last_geofence_alert[zone_name] = time.time()

        msg = f"Zone violation: {object_class} entered '{zone_name}'"

        return {
            "type": "GEOFENCE",
            "message": msg,
            "text": msg,
            "description": msg,
            "timestamp": time.strftime("%H:%M:%S"),
            "zone": zone_name,
            "object": object_class,
        }


# Global instance
alert_manager = AlertManager()

# Shared state
state = {
    "streaming_active": False,
    "geofence_enabled": False,
    "zones": [],
    "last_alert_time": 0
}
