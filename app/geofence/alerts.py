import time

class AlertManager:
    def __init__(self, cooldown=15):
        self.cooldown = cooldown
        self.last_alert = 0

    def can_alert(self):
        return time.time() - self.last_alert > self.cooldown

    def trigger(self, message):
        self.last_alert = time.time()
        return {
            "message": message,
            "timestamp": time.strftime("%H:%M:%S")
        }
