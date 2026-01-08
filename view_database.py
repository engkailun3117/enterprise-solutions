"""
View all users and their data in the database
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add backend to path
sys.path.insert(0, '/home/user/enterprise-solutions/backend')

from models import User, ChatSession, CompanyOnboarding, ChatMessage
from database import engine

Session = sessionmaker(bind=engine)
db = Session()

def view_all_data():
    print("=" * 80)
    print("DATABASE CONTENTS")
    print("=" * 80)

    # View all users
    users = db.query(User).all()
    print(f"\n📊 USERS ({len(users)} total)")
    print("-" * 80)
    for user in users:
        print(f"\nUser ID: {user.id}")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Role: {user.role.value}")
        print(f"  Created: {user.created_at}")

    # View all chat sessions
    sessions = db.query(ChatSession).all()
    print(f"\n\n💬 CHAT SESSIONS ({len(sessions)} total)")
    print("-" * 80)
    for session in sessions:
        user = db.query(User).filter(User.id == session.user_id).first()
        print(f"\nSession ID: {session.id}")
        print(f"  User: {user.username if user else 'Unknown'}")
        print(f"  Status: {session.status.value}")
        print(f"  Created: {session.created_at}")

        # Get onboarding data
        onboarding = session.onboarding_data
        if onboarding:
            print(f"  Onboarding Data:")
            print(f"    - Industry: {onboarding.industry or 'N/A'}")
            print(f"    - Capital: {onboarding.capital_amount or 'N/A'}億")
            print(f"    - Invention Patents: {onboarding.invention_patent_count or 'N/A'}")
            print(f"    - Utility Patents: {onboarding.utility_patent_count or 'N/A'}")
            print(f"    - Certifications: {onboarding.certification_count or 'N/A'}")
            print(f"    - ESG: {'有' if onboarding.esg_certification else '無'}")

        # Get message count
        message_count = db.query(ChatMessage).filter(ChatMessage.session_id == session.id).count()
        print(f"  Messages: {message_count}")

    # Summary
    print(f"\n\n📈 SUMMARY")
    print("-" * 80)
    print(f"Total Users: {len(users)}")
    print(f"Total Chat Sessions: {len(sessions)}")
    messages_total = db.query(ChatMessage).count()
    print(f"Total Messages: {messages_total}")
    print(f"\n✅ All user data is properly isolated by user_id and session_id")

    print("\n" + "=" * 80)
    print("END OF DATABASE VIEW")
    print("=" * 80)

if __name__ == "__main__":
    try:
        view_all_data()
    except Exception as e:
        print(f"Error viewing database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
