import time

# Use a dictionary for mutable shared state
state = {
    "streaming_active": False,
    "last_alert_time": 0
}

ALERT_COOLDOWN_SECONDS = 15
