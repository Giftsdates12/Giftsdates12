#!/usr/bin/env python3
"""
Backend API Testing for GiftsDates
Tests core authentication flow: register -> login -> authenticated endpoints
"""
import requests
import json
import uuid
from datetime import datetime

# Backend URL from frontend/.env
BACKEND_URL = "https://login-saver-web.preview.emergentagent.com/api"

def print_test(name, passed, details=""):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {name}")
    if details:
        print(f"   {details}")
    print()

def test_health_check():
    """Test that backend is responding"""
    print("=" * 60)
    print("TEST 1: Backend Health Check")
    print("=" * 60)
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        data = response.json()
        passed = response.status_code == 200 and data.get("service") == "GiftsDates" and data.get("ok") == True
        print_test("GET /api/ health check", passed, f"Response: {data}")
        return passed
    except Exception as e:
        print_test("GET /api/ health check", False, f"Error: {str(e)}")
        return False

def test_register():
    """Test user registration"""
    print("=" * 60)
    print("TEST 2: User Registration")
    print("=" * 60)
    
    # Generate unique email for this test
    unique_id = str(uuid.uuid4())[:8]
    test_email = f"testuser_{unique_id}@example.com"
    
    payload = {
        "email": test_email,
        "password": "SecurePass123!",
        "name": "Test User",
        "age": 28,
        "gender": "female",
        "interested_in": "male",
        "orientation": "straight",
        "city": "New York",
        "country": "USA",
        "bio": "Testing the GiftsDates auth flow",
        "language": "en"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/register", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            user = data.get("user")
            
            # Validate response structure
            has_token = bool(token)
            has_user = bool(user)
            email_matches = user.get("email") == test_email if user else False
            has_id = bool(user.get("id")) if user else False
            
            passed = has_token and has_user and email_matches and has_id
            
            details = f"Token: {'Present' if has_token else 'Missing'}, User ID: {user.get('id') if user else 'N/A'}, Email: {user.get('email') if user else 'N/A'}"
            print_test("POST /api/auth/register", passed, details)
            
            return passed, token, user.get("id") if user else None, test_email
        else:
            print_test("POST /api/auth/register", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
            return False, None, None, test_email
            
    except Exception as e:
        print_test("POST /api/auth/register", False, f"Error: {str(e)}")
        return False, None, None, test_email

def test_login(email, password="SecurePass123!"):
    """Test user login"""
    print("=" * 60)
    print("TEST 3: User Login")
    print("=" * 60)
    
    payload = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            user = data.get("user")
            
            has_token = bool(token)
            has_user = bool(user)
            email_matches = user.get("email") == email if user else False
            
            passed = has_token and has_user and email_matches
            
            details = f"Token: {'Present' if has_token else 'Missing'}, User: {user.get('name') if user else 'N/A'}, Email: {user.get('email') if user else 'N/A'}"
            print_test("POST /api/auth/login", passed, details)
            
            return passed, token
        else:
            print_test("POST /api/auth/login", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
            return False, None
            
    except Exception as e:
        print_test("POST /api/auth/login", False, f"Error: {str(e)}")
        return False, None

def test_authenticated_endpoint(token):
    """Test authenticated endpoint with JWT token"""
    print("=" * 60)
    print("TEST 4: Authenticated Endpoint (GET /api/auth/me)")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(f"{BACKEND_URL}/auth/me", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            has_id = bool(data.get("id"))
            has_email = bool(data.get("email"))
            has_name = bool(data.get("name"))
            
            passed = has_id and has_email and has_name
            
            details = f"User ID: {data.get('id')}, Name: {data.get('name')}, Email: {data.get('email')}"
            print_test("GET /api/auth/me (authenticated)", passed, details)
            
            return passed
        else:
            print_test("GET /api/auth/me (authenticated)", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print_test("GET /api/auth/me (authenticated)", False, f"Error: {str(e)}")
        return False

def test_meta_endpoint():
    """Test public meta endpoint"""
    print("=" * 60)
    print("TEST 5: Public Endpoint (GET /api/meta)")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BACKEND_URL}/meta", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            has_gifts = "gifts" in data
            has_packages = "coin_packages" in data
            has_premium = "premium" in data
            
            passed = has_gifts and has_packages and has_premium
            
            details = f"Gifts: {len(data.get('gifts', []))}, Coin Packages: {len(data.get('coin_packages', []))}, Premium: ${data.get('premium', {}).get('amount', 'N/A')}"
            print_test("GET /api/meta (public)", passed, details)
            
            return passed
        else:
            print_test("GET /api/meta (public)", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print_test("GET /api/meta (public)", False, f"Error: {str(e)}")
        return False

def test_support_config():
    """Test support config endpoint"""
    print("=" * 60)
    print("TEST 6: Support Config Endpoint (GET /api/support/config)")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BACKEND_URL}/support/config", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            has_welcome = "welcome_message" in data
            has_hours = "hours" in data
            has_status = "is_open" in data
            
            passed = has_welcome and has_hours and has_status
            
            details = f"Support Open: {data.get('is_open', 'N/A')}, Hours configured: {len(data.get('hours', []))} days"
            print_test("GET /api/support/config (public)", passed, details)
            
            return passed
        else:
            print_test("GET /api/support/config (public)", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print_test("GET /api/support/config (public)", False, f"Error: {str(e)}")
        return False

def test_spin_config():
    """Test spin-to-win config endpoint"""
    print("=" * 60)
    print("TEST 7: Spin Config Endpoint (GET /api/spin/config)")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BACKEND_URL}/spin/config", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            has_prizes = "prizes" in data
            prizes_count = len(data.get("prizes", []))
            
            passed = has_prizes and prizes_count > 0
            
            details = f"Prizes available: {prizes_count}"
            print_test("GET /api/spin/config (public)", passed, details)
            
            return passed
        else:
            print_test("GET /api/spin/config (public)", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print_test("GET /api/spin/config (public)", False, f"Error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("GIFTSDATES BACKEND API TESTING")
    print("Testing Core Authentication Flow")
    print("=" * 60 + "\n")
    
    results = []
    
    # Test 1: Health check
    results.append(("Health Check", test_health_check()))
    
    # Test 2: Register new user
    register_passed, token, user_id, test_email = test_register()
    results.append(("User Registration", register_passed))
    
    # Test 3: Login with registered user
    if register_passed and test_email:
        login_passed, login_token = test_login(test_email)
        results.append(("User Login", login_passed))
        
        # Use the login token for authenticated tests
        if login_passed and login_token:
            token = login_token
    else:
        results.append(("User Login", False))
    
    # Test 4: Authenticated endpoint
    if token:
        results.append(("Authenticated Endpoint", test_authenticated_endpoint(token)))
    else:
        print("=" * 60)
        print("TEST 4: Authenticated Endpoint - SKIPPED (no token)")
        print("=" * 60 + "\n")
        results.append(("Authenticated Endpoint", False))
    
    # Test 5-7: Public endpoints
    results.append(("Meta Endpoint", test_meta_endpoint()))
    results.append(("Support Config", test_support_config()))
    results.append(("Spin Config", test_spin_config()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "-" * 60)
    print(f"Total: {passed_count}/{total_count} tests passed")
    print("=" * 60 + "\n")
    
    # Return exit code
    return 0 if passed_count == total_count else 1

if __name__ == "__main__":
    exit(main())
