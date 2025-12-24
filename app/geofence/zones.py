from dataclasses import dataclass
from typing import List, Tuple
import json
from shapely.geometry import Polygon

@dataclass
class Zone:
    name: str
    polygon: Polygon
    color: Tuple[int, int, int]
    alpha: float

def load_zones(path: str) -> List[Zone]:
    with open(path, "r") as f:
        data = json.load(f)

    zones = []
    for z in data:
        zones.append(
            Zone(
                name=z["name"],
                polygon=Polygon(z["points"]),
                color=tuple(z["color"]),
                alpha=z["alpha"]
            )
        )
    return zones
