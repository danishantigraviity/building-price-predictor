import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000/api"

def test_api():
    print("Testing API...")
    
    # 1. Login
    try:
        # Use credentials from config or register new
        # Let's try to register a temp user first
        reg_payload = {"username": "testapi", "email": "testapi@example.com", "password": "password123"}
        resp = requests.post(f"{BASE_URL}/auth/register", json=reg_payload)
        
        if resp.status_code == 201:
            print("✅ Register Success")
        elif resp.status_code == 400 and "taken" in resp.text:
            print("ℹ️ User exists, proceeding to login")
            
        # Login
        login_payload = {"email": "testapi@example.com", "password": "password123"}
        resp = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
        
        if resp.status_code == 200:
            token = resp.json().get('access_token')
            print("✅ Login Success, Token received")
        else:
            print(f"❌ Login Failed: {resp.text}")
            return

        # 2. Access Protected Route (Dashboard)
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{BASE_URL}/data/dashboard", headers=headers)
        
        if resp.status_code == 200:
            print("✅ Dashboard Access Success")
            print(f"   Count: {resp.json().get('count')}")
        else:
            print(f"❌ Dashboard Failed: {resp.text}")
            
        # 3. Estimate
        est_payload = {
            "city": "Chennai",
            "quality": "premium",
            "floors": 2,
            "area_sqft": 1000
        }
        resp = requests.post(f"{BASE_URL}/data/estimate", json=est_payload, headers=headers)
        if resp.status_code == 201:
            print("✅ Estimation Success")
            print(f"   Total Cost: {resp.json().get('total_cost')}")
        else:
            print(f"❌ Estimation Failed: {resp.text}")

    except Exception as e:
        print(f"❌ Test Failed with Exception: {e}")

if __name__ == "__main__":
    # Wait for server to start if ran swiftly
    time.sleep(2) 
    test_api()
