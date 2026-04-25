import numpy as np
import cv2
from .rules import rule_matches

class GeofenceEngine:
    """Checks if detected objects violate geofence zones using high-speed vectorized masks"""
    
    def __init__(self, ioa_threshold=0.3):
        self.ioa_threshold = ioa_threshold
        self.masks = {} # dict of zone_name -> binary numpy mask
        self.zone_hashes = {} # to track changes in zones

    def _get_zone_hash(self, zone_data, frame_shape):
        """Simple hash to detect if a zone changed without rebuilding masks unnecessarily"""
        points_tuple = tuple((p[0], p[1]) for p in zone_data.get("points", []))
        return hash((zone_data["name"], points_tuple, frame_shape))

    def update_zones(self, zones_data, frame_shape):
        """
        Renders binary masks for zones. Only computes mask if the zone is new or changed.
        Args:
            zones_data: list of dicts like {"name": "z1", "points": [[x,y],...]}
            frame_shape: (height, width) or (height, width, channels)
        """
        h, w = frame_shape[:2]
        current_names = set()
        
        for z in zones_data:
            name = z.get("name")
            if not name or not z.get("points") or len(z["points"]) < 3:
                continue
            
            current_names.add(name)
            zone_hash = self._get_zone_hash(z, frame_shape)
            
            # If mask doesn't exist or zone changed, re-render via cv2.fillPoly
            if name not in self.masks or self.zone_hashes.get(name) != zone_hash:
                mask = np.zeros((h, w), dtype=np.uint8)
                points = np.array(z["points"], dtype=np.int32)
                
                cv2.fillPoly(mask, [points], 1)
                
                self.masks[name] = mask
                self.zone_hashes[name] = zone_hash

        # Clean up deleted zones
        keys_to_remove = [k for k in self.masks.keys() if k not in current_names]
        for k in keys_to_remove:
            del self.masks[k]
            del self.zone_hashes[k]

    def process(self, detections, frame_shape, zones_data):
        """
        Check detections against masks using Intersection over Area (IoA)
        Args:
            detections: List of dicts {"class": str, "bbox": (x1, y1, x2, y2)}
            frame_shape: Shape of the current frame
            zones_data: List of zone configurations
        Returns:
            Dict of zone_name -> list of violating object classes
        """
        self.update_zones(zones_data, frame_shape)
        
        violations = {} 
        
        if not self.masks or not detections:
            return violations
            
        h, w = frame_shape[:2]
        
        for det in detections:
            bbox = det.get("bbox")
            if not bbox: continue
            
            x1, y1, x2, y2 = bbox
            # Constrain to frame boundaries
            x1, y1 = max(0, int(x1)), max(0, int(y1))
            x2, y2 = min(w, int(x2)), min(h, int(y2))
            
            box_area = (x2 - x1) * (y2 - y1)
            if box_area <= 0:
                continue
                
            # Vectorized overlap check using Numpy array slicing
            for zone_name, mask in self.masks.items():
                if rule_matches(zone_name, det["class"]):
                    # Slice the exact part of the mask that the bbox covers
                    box_mask = mask[y1:y2, x1:x2]
                    
                    # Sum the 1s to get the intersection area
                    intersection_area = np.sum(box_mask)
                    
                    ioa = intersection_area / box_area
                    
                    if ioa > self.ioa_threshold:
                        if zone_name not in violations:
                            violations[zone_name] = []
                        violations[zone_name].append(det["class"])
                        
        return violations