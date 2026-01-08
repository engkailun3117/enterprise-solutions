"""
Get login credentials for test users
"""
import requests

BASE_URL = "http://localhost:8000"

# Test user credentials
test_users = {
    "1": {"username": "testuser1", "email": "test1@example.com", "password": "password123"},
    "2": {"username": "testuser2", "email": "test2@example.com", "password": "password123"},
    "3": {"username": "testuser3", "email": "test3@example.com", "password": "password123"},
    "4": {"username": "company_a_user", "email": "companyA@test.com", "password": "pass123"},
    "5": {"username": "company_b_user", "email": "companyB@test.com", "password": "pass123"},
    "6": {"username": "company_c_user", "email": "companyC@test.com", "password": "pass123"},
}

print("=" * 70)
print("TEST USER LOGIN CREDENTIALS")
print("=" * 70)
print("\nAvailable test users:\n")

for num, user in test_users.items():
    print(f"{num}. {user['username']}")
    print(f"   Email: {user['email']}")
    print(f"   Password: {user['password']}")
    print()

print("=" * 70)
print("HOW TO USE:")
print("=" * 70)
print("\n1. Start the frontend:")
print("   cd /home/user/enterprise-solutions/frontend")
print("   npm run dev")
print("\n2. Open browser: http://localhost:3000")
print("\n3. Login with any of the credentials above")
print("\n4. Each user has their own isolated data")
print("\n" + "=" * 70)

# Test login for one user
print("\nTesting login for testuser1...")
response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "username": "testuser1",
    "password": "password123"
})

if response.status_code == 200:
    result = response.json()
    print("✓ Login successful!")
    print(f"  Token: {result['access_token'][:50]}...")
    print(f"  User ID: {result['user']['id']}")
    print(f"  Role: {result['user']['role']}")
else:
    print("✗ Login failed")

print("\n" + "=" * 70)
