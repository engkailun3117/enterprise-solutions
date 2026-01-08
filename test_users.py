"""
Test script to register multiple users and verify login functionality
"""
import requests
import json
from typing import List, Dict

BASE_URL = "http://localhost:8000"

class UserTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.test_users = []

    def register_user(self, username: str, email: str, password: str) -> Dict:
        """Register a new user"""
        url = f"{self.base_url}/api/auth/register"
        data = {
            "username": username,
            "email": email,
            "password": password
        }

        try:
            response = requests.post(url, json=data)
            if response.status_code == 201:
                result = response.json()
                print(f"✓ Successfully registered user: {username}")
                print(f"  Email: {email}")
                print(f"  Token: {result['access_token'][:30]}...")
                return result
            else:
                print(f"✗ Failed to register {username}: {response.status_code}")
                print(f"  Error: {response.json()}")
                return None
        except Exception as e:
            print(f"✗ Error registering {username}: {e}")
            return None

    def login_user(self, username: str, password: str) -> Dict:
        """Login as a user"""
        url = f"{self.base_url}/api/auth/login"
        data = {
            "username": username,
            "password": password
        }

        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Successfully logged in as: {username}")
                print(f"  Role: {result['user']['role']}")
                return result
            else:
                print(f"✗ Failed to login {username}: {response.status_code}")
                print(f"  Error: {response.json()}")
                return None
        except Exception as e:
            print(f"✗ Error logging in {username}: {e}")
            return None

    def get_user_profile(self, token: str) -> Dict:
        """Get current user profile"""
        url = f"{self.base_url}/api/users/me"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"✗ Failed to get profile: {response.status_code}")
                return None
        except Exception as e:
            print(f"✗ Error getting profile: {e}")
            return None

    def create_chat_session(self, token: str, use_ai: bool = False) -> Dict:
        """Create a new chat session"""
        url = f"{self.base_url}/api/chatbot/sessions/new"
        headers = {"Authorization": f"Bearer {token}"}
        data = {"use_ai": use_ai}

        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"✗ Failed to create session: {response.status_code}")
                return None
        except Exception as e:
            print(f"✗ Error creating session: {e}")
            return None

    def run_full_test(self):
        """Run comprehensive test with multiple users"""
        print("=" * 60)
        print("Starting User Registration and Login Tests")
        print("=" * 60)

        # Define test users
        test_users = [
            {"username": "testuser1", "email": "test1@example.com", "password": "password123"},
            {"username": "testuser2", "email": "test2@example.com", "password": "password123"},
            {"username": "testuser3", "email": "test3@example.com", "password": "password123"},
        ]

        user_tokens = {}

        # Step 1: Register all users
        print("\n" + "=" * 60)
        print("STEP 1: Registering Users")
        print("=" * 60)
        for user in test_users:
            result = self.register_user(user["username"], user["email"], user["password"])
            if result:
                user_tokens[user["username"]] = result["access_token"]
            print()

        # Step 2: Test login for each user
        print("=" * 60)
        print("STEP 2: Testing Login")
        print("=" * 60)
        for user in test_users:
            result = self.login_user(user["username"], user["password"])
            if result and user["username"] not in user_tokens:
                user_tokens[user["username"]] = result["access_token"]
            print()

        # Step 3: Verify user profiles
        print("=" * 60)
        print("STEP 3: Verifying User Profiles")
        print("=" * 60)
        for username, token in user_tokens.items():
            print(f"\nChecking profile for: {username}")
            profile = self.get_user_profile(token)
            if profile:
                print(f"  ✓ Username: {profile['username']}")
                print(f"  ✓ Email: {profile['email']}")
                print(f"  ✓ Role: {profile['role']}")
                print(f"  ✓ Active: {profile['is_active']}")

        # Step 4: Create chat sessions for each user
        print("\n" + "=" * 60)
        print("STEP 4: Creating Chat Sessions")
        print("=" * 60)
        for username, token in user_tokens.items():
            print(f"\nCreating session for: {username}")
            session = self.create_chat_session(token)
            if session:
                print(f"  ✓ Session ID: {session['session_id']}")
                print(f"  ✓ Progress: {session['progress']['fields_completed']}/{session['progress']['total_fields']}")

        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        print(f"Total users registered/logged in: {len(user_tokens)}")
        print(f"All users have unique tokens: {len(set(user_tokens.values())) == len(user_tokens)}")
        print("\nTest completed successfully!" if len(user_tokens) == len(test_users) else "\nSome tests failed!")
        print("=" * 60)

        return user_tokens

if __name__ == "__main__":
    tester = UserTester()
    tester.run_full_test()
