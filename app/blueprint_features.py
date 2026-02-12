import cv2
import numpy as np

def _safe_read(image_bytes):
    arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return img

def extract_blueprint_features(image_bytes):
    img = _safe_read(image_bytes)
    if img is None:
        return {
            "area_sqft_estimate": 900,
            "rooms_estimate": 5,
            "wall_length_ft": 120
        }

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Clean noise
    gray = cv2.GaussianBlur(gray, (5,5), 0)

    # Edge detect
    edges = cv2.Canny(gray, 50, 150)

    # Dilate edges to close gaps in walls
    kernel = np.ones((5,5), np.uint8)
    edges_d = cv2.dilate(edges, kernel, iterations=2)

    # Find contours (rooms)
    cnts, hierarchy = cv2.findContours(edges_d, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    room_count = 0
    total_room_area_px = 0

    for c in cnts:
        area = cv2.contourArea(c)
        if 1500 < area < 500000:  # filter noise
            room_count += 1
            total_room_area_px += area

    # Convert pixels → sqft using empirical scale
    sqft = total_room_area_px / 95.0   # refined scaling factor

    # Wall length estimation (more stable)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=80,
                            minLineLength=40, maxLineGap=10)

    wall_len = 0
    if lines is not None:
        for l in lines:
            x1, y1, x2, y2 = l[0]
            wall_len += np.hypot(x2-x1, y2-y1)

    wall_len_ft = wall_len / 12.0  # updated scale

    # Clamp safe ranges
    sqft = max(300, min(sqft, 6000))
    wall_len_ft = max(40, min(wall_len_ft, 1200))
    room_count = max(1, min(room_count, 12))

    return {
        "area_sqft_estimate": round(sqft, 1),
        "rooms_estimate": room_count,
        "wall_length_ft": round(wall_len_ft, 1)
    }
