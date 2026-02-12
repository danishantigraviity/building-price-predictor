import cv2
import numpy as np
import pytesseract
import re

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_blueprint_features(image_bytes):
    # Read image
    arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    if img is None:
        return {
            "area_sqft_estimate": 900,
            "rooms_estimate": 5,
            "wall_length_ft": 120
        }

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # OCR to extract numbers from blueprint
    text = pytesseract.image_to_string(gray)

    # Find cm values (e.g., 350 cm, 400cm)
    cm_values = re.findall(r"(\d+)\s*cm", text)

    cm_values = [int(v) for v in cm_values]

    # If no measurements detected, fall back
    if len(cm_values) < 2:
        return {
            "area_sqft_estimate": 900,
            "rooms_estimate": 5,
            "wall_length_ft": 120
        }

    # Convert cm → feet
    total_sqft = 0
    for cm in cm_values:
        ft = cm * 0.0328084    # cm → feet
        sqft = ft * ft         # rough heuristic per room
        total_sqft += sqft

    # Estimate number of rooms from count of dimensions
    rooms = max(1, len(cm_values) // 2)

    # Wall length estimation (simple)
    wall_length = sum(cm_values) * 0.0328084

    return {
        "area_sqft_estimate": round(total_sqft, 1),
        "rooms_estimate": rooms,
        "wall_length_ft": round(wall_length, 1)
    }
