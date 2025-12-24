"""
Geometry helper functions for geofencing
"""


def bbox_feet(x1, y1, x2, y2):
    """
    Get feet position (bottom-center) of bounding box
    
    Args:
        x1, y1, x2, y2: Bounding box coordinates
    
    Returns:
        (cx, cy): Center-x, bottom-y coordinates
    """
    cx = (x1 + x2) / 2
    cy = y2  # Bottom of bbox
    return cx, cy


def point_in_zone(point, zone):
    """
    Check if a point is inside a zone polygon
    
    Args:
        point: (x, y) tuple
        zone: Zone object with polygon attribute
    
    Returns:
        bool: True if point is inside zone
    """
    from shapely.geometry import Point
    
    p = Point(point[0], point[1])
    return zone.polygon.contains(p)