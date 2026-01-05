#!/usr/bin/env python3
"""
Script to create an admin user for the Supplier Onboarding Platform.
Run this after setting up the database to create your first admin account.
"""

from database import SessionLocal
from models import User, UserRole
from auth import get_password_hash
import sys


def create_admin_user(username: str, email: str, password: str):
    """Create an admin user in the database"""
    db = SessionLocal()

    try:
        # Check if username already exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"❌ Error: Username '{username}' already exists!")
            print(f"   User ID: {existing_user.id}, Role: {existing_user.role.value}")

            # Offer to promote existing user
            if existing_user.role != UserRole.ADMIN:
                promote = input(f"\nWould you like to promote '{username}' to admin? (yes/no): ")
                if promote.lower() in ['yes', 'y']:
                    existing_user.role = UserRole.ADMIN
                    db.commit()
                    print(f"✅ User '{username}' has been promoted to admin!")
                    return True
            return False

        # Check if email already exists
        existing_email = db.query(User).filter(User.email == email).first()
        if existing_email:
            print(f"❌ Error: Email '{email}' is already registered!")
            print(f"   Username: {existing_email.username}")
            return False

        # Create new admin user
        admin = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            role=UserRole.ADMIN
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print(f"✅ Admin user created successfully!")
        print(f"   ID: {admin.id}")
        print(f"   Username: {admin.username}")
        print(f"   Email: {admin.email}")
        print(f"   Role: {admin.role.value}")
        print(f"\nYou can now login with:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")

        return True

    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {str(e)}")
        return False

    finally:
        db.close()


def main():
    """Main function with interactive prompts"""
    print("=" * 60)
    print("  Supplier Onboarding Platform - Admin User Creation")
    print("=" * 60)
    print()

    # Check if command line arguments provided
    if len(sys.argv) == 4:
        username, email, password = sys.argv[1], sys.argv[2], sys.argv[3]
        print(f"Creating admin user from command line arguments...")
    else:
        # Interactive mode
        print("Please enter admin user details:")
        username = input("Username: ").strip()
        email = input("Email: ").strip()
        password = input("Password: ").strip()

        # Validation
        if len(username) < 3:
            print("❌ Username must be at least 3 characters!")
            return

        if '@' not in email:
            print("❌ Invalid email address!")
            return

        if len(password) < 6:
            print("❌ Password must be at least 6 characters!")
            return

    print()
    print("Creating admin user...")
    print("-" * 60)

    success = create_admin_user(username, email, password)

    if success:
        print()
        print("=" * 60)
        print("✅ Setup complete! You can now login to the admin panel.")
        print("=" * 60)
    else:
        print()
        print("=" * 60)
        print("❌ Failed to create admin user. Please check the errors above.")
        print("=" * 60)


if __name__ == "__main__":
    main()
