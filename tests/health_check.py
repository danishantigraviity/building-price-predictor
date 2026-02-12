import requests
import sys

BASE_URL = "http://127.0.0.1:5000"

def check_endpoint(url, method="GET", expected_status=200):
    try:
        response = requests.request(method, url, timeout=5)
        if response.status_code == expected_status:
            print(f"✅ {method} {url} - OK ({response.status_code})")
            return True
        else:
            print(f"❌ {method} {url} - FAILED (Expected {expected_status}, got {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {method} {url} - ERROR ({e})")
        return False

def run_tests():
    print("🚀 Starting API Health Checks...")
    
    # 1. Public Routes
    checks = [
        (f"{BASE_URL}/", "GET", 200), # Serving React App
        (f"{BASE_URL}/dashboard", "GET", 200), # SPA route check
        (f"{BASE_URL}/api/auth/me", "GET", 401), # Unauthorized by default (confirms route exists)
        (f"{BASE_URL}/assets/index-DbzXe99x.js", "GET", 200) # Latest Results fix bundle
    ]
    
    success = True
    for url, method, status in checks:
        if not check_endpoint(url, method, status):
            success = False
            
    if success:
        print("\n🎉 All health checks passed!")
        sys.exit(0)
    else:
        print("\n⚠️ Some health checks failed.")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
