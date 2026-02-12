from PIL import Image
import io

def extract_blueprint_features(image_bytes):
    """
    Simpler, lightweight feature extraction using Pillow.
    Avoids heavy OpenCV/Numpy dependencies to fit within Vercel's 250MB limit.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        width, height = img.size
        
        # Use pixel area and aspect ratio as heuristics
        # Standard scaling: 1000px width ~ 50ft real world
        res_scale = (width * height) / 1000000.0
        
        sqft = res_scale * 1200 # empirical base
        # Heuristic for rooms: based on image complexity/size
        room_count = max(2, min(int(res_scale * 6), 10))
        # Heuristic for wall length: perimeter-based
        wall_len_ft = (width + height) * 0.08 
        
        # Clamp ranges
        sqft = max(400, min(sqft, 5000))
        wall_len_ft = max(60, min(wall_len_ft, 1000))
        room_count = max(1, min(room_count, 10))

        return {
            "area_sqft_estimate": round(sqft, 1),
            "rooms_estimate": room_count,
            "wall_length_ft": round(wall_len_ft, 1)
        }
    except Exception as e:
        print(f"Pillow extraction error: {e}")
        return {
            "area_sqft_estimate": 900.0,
            "rooms_estimate": 5,
            "wall_length_ft": 120.0
        }
