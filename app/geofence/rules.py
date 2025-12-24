"""
Geofence rules - defines which objects trigger alerts in which zones
"""

# Default: Alert for all person detections
RESTRICTED_CLASSES = ["person"]


def rule_matches(zone_name, object_class):
    """
    Check if an object class should trigger alert in a zone
    
    Args:
        zone_name: Name of the zone
        object_class: Detected object class (e.g., "person", "car")
    
    Returns:
        bool: True if this detection should trigger an alert
    """
    
    # Default behavior: Alert for any person in any restricted zone
    if object_class in RESTRICTED_CLASSES:
        return True
    
    # You can add custom rules per zone here:
    # if zone_name == "vehicle_only":
    #     return object_class == "person"  # Only alert if person enters
    # elif zone_name == "no_vehicles":
    #     return object_class in ["car", "truck", "motorcycle"]
    
    return False