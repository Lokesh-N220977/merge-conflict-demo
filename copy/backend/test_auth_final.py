import requests
import uuid

BASE_URL = "http://127.0.0.1:8000/api"

def test_auth_flow():
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    
    print(f"--- Testing with email: {email} ---")

    # 1. Access /profile without token (Should fail 401)
    print("1. Testing unauthorized access to /profile...")
    resp = requests.get(f"{BASE_URL}/profile")
    if resp.status_code == 401:
        print("PASS: Unauthorized access blocked with 401.")
    else:
        print(f"FAIL: Unauthorized access returned {resp.status_code}. Response: {resp.text}")

    # 2. Register user
    print("2. Registering new user...")
    reg_data = {
        "name": "Test User",
        "email": email,
        "password": password,
        "phone": "1234567890",
        "role": "patient"
    }
    resp = requests.post(f"{BASE_URL}/register", json=reg_data)
    if resp.status_code == 200:
        print("PASS: User registered successfully.")
    else:
        print(f"FAIL: Registration failed with {resp.status_code}. Response: {resp.text}")
        return

    # 3. Login
    print("3. Logging in...")
    login_data = {"email": email, "password": password}
    resp = requests.post(f"{BASE_URL}/login", json=login_data)
    if resp.status_code == 200:
        token = resp.json().get("access_token")
        print("PASS: Login successful. Token obtained.")
    else:
        print(f"FAIL: Login failed with {resp.status_code}. Response: {resp.text}")
        return

    # 4. Access /profile with token
    print("4. Testing authorized access to /profile...")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/profile", headers=headers)
    if resp.status_code == 200:
        print("PASS: Profile accessed successfully.")
        print(f"Profile Data: {resp.json()}")
    else:
        print(f"FAIL: Profile access failed with {resp.status_code}. Response: {resp.text}")

if __name__ == "__main__":
    try:
        test_auth_flow()
    except Exception as e:
        print(f"An error occurred during testing: {e}")
