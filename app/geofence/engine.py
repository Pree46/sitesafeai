from .geometry import bbox_feet, point_in_zone
from .rules import rule_matches


class GeofenceEngine:
    """Checks if detected objects violate geofence zones"""
    
    def __init__(self, zones, alert_manager=None):
        self.zones = zones
        self.alerts = alert_manager

    def process_detections(self, detections):
        """
        Check detections against zones
        
        Args:
            detections: List of {"class": str, "bbox": (x1,y1,x2,y2)}
        
        Returns:
            List of {"zone": str, "object": str} violations
        """
        violations = []

        for det in detections:
            # Get feet position (bottom-center of bbox)
            cx, cy = bbox_feet(*det["bbox"])

            # Check against each zone
            for zone in self.zones:
                if point_in_zone((cx, cy), zone):
                    # Check if this class is restricted in this zone
                    if rule_matches(zone.name, det["class"]):
                        violations.append({
                            "zone": zone.name,
                            "object": det["class"]
                        })

        return violations

    def evaluate(self, detections):
        """Backward compatibility alias"""
        return self.process_detections(detections)