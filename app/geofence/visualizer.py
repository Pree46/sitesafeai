def draw_zones(frame, zones):
    overlay = frame.copy()

    for z in zones:
        pts = np.array(z.polygon.exterior.coords, dtype=np.int32)
        cv2.fillPoly(overlay, [pts], z.color)
        cv2.polylines(overlay, [pts], True, z.color, 3)

    return cv2.addWeighted(overlay, 0.4, frame, 0.6, 0)
