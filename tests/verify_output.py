import requests
import json

BASE_URL = "http://127.0.0.1:5000"

import time

def test_full_flow():
    uid = int(time.time())
    email = f"test_{uid}@example.com"
    username = f"user_{uid}"
    print(f"📝 Registering new user: {username} ({email})...")
    reg_res = requests.post(f"{BASE_URL}/api/auth/register", json={
        "username": username,
        "email": email,
        "password": "password123"
    })
    
    if reg_res.status_code not in [200, 201]:
        print(f"❌ Registration failed: {reg_res.text}")
        return

    token = reg_res.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Registration successful.")

    print("\n📊 Sending Estimation Request (Chennai, Standard, 2 Floors, Area: 1200sqft)...")
    est_data = {
        "city": "Chennai",
        "quality": "standard",
        "floors": 2,
        "area_sqft": 1200,
        "rooms": 5
    }
    
    # Use JSON for the test script as data.py handles is_json
    est_res = requests.post(f"{BASE_URL}/api/data/estimate", json=est_data, headers=headers)
    
    if est_res.status_code == 201:
        res_data = est_res.json()
        print(f"\n🎉 SUCCESS! Estimation Created (ID: {res_data['id']})")
        
        print(f"\n🔍 Verifying Result Retrieval for ID: {res_data['id']}...")
        get_res = requests.get(f"{BASE_URL}/api/data/result/{res_data['id']}", headers=headers)
        
        if get_res.status_code == 200:
            print("✅ Result retrieval successful!")
            print(json.dumps(get_res.json(), indent=4))
        else:
            print(f"❌ Result retrieval failed: {get_res.status_code}")
            print(f"Response: {get_res.text}")
    else:
        print(f"\n❌ Estimation creation failed: {est_res.status_code}")
        print(f"Response: {est_res.text}")

if __name__ == "__main__":
    test_full_flow()
