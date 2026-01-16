"""
Migration script to update ESG certification schema and clear all data
"""

from sqlalchemy import create_engine, text
from config import get_settings

settings = get_settings()

def migrate():
    """Update ESG certification schema and clear all data"""
    engine = create_engine(settings.database_url)

    with engine.connect() as conn:
        trans = conn.begin()

        try:
            print("=" * 60)
            print("ESG CERTIFICATION SCHEMA UPDATE & DATA CLEANUP")
            print("=" * 60)

            # Step 1: Delete all data
            print("\n🗑️  Step 1: Deleting all data...")

            # Delete in correct order (respecting foreign keys)
            conn.execute(text("TRUNCATE TABLE products CASCADE"))
            print("   ✓ Deleted all products")

            conn.execute(text("TRUNCATE TABLE company_onboarding CASCADE"))
            print("   ✓ Deleted all company onboarding data")

            conn.execute(text("TRUNCATE TABLE chat_messages CASCADE"))
            print("   ✓ Deleted all chat messages")

            conn.execute(text("TRUNCATE TABLE chat_sessions CASCADE"))
            print("   ✓ Deleted all chat sessions")

            print("   ✓ All data cleared successfully")

            # Step 2: Update schema
            print("\n🔧 Step 2: Updating ESG certification schema...")

            # Drop old esg_certification (boolean) column
            print("   - Dropping old esg_certification (boolean) column...")
            conn.execute(text("""
                ALTER TABLE company_onboarding
                DROP COLUMN IF EXISTS esg_certification
            """))
            print("   ✓ Dropped old column")

            # Add new esg_certification_count (integer) column
            print("   - Adding esg_certification_count (integer) column...")
            conn.execute(text("""
                ALTER TABLE company_onboarding
                ADD COLUMN IF NOT EXISTS esg_certification_count INTEGER
            """))
            print("   ✓ Added esg_certification_count column")

            # Add new esg_certification (text) column
            print("   - Adding esg_certification (text) column...")
            conn.execute(text("""
                ALTER TABLE company_onboarding
                ADD COLUMN IF NOT EXISTS esg_certification TEXT
            """))
            print("   ✓ Added esg_certification column")

            # Step 3: Verify schema
            print("\n🔍 Step 3: Verifying new schema...")
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'company_onboarding'
                AND column_name IN ('certification_count', 'esg_certification_count', 'esg_certification')
                ORDER BY ordinal_position
            """))

            print("\n   Current Schema:")
            print("   " + "-" * 50)
            print("   Column Name                | Type      | Nullable")
            print("   " + "-" * 50)
            for row in result:
                print(f"   {row[0]:26} | {row[1]:9} | {row[2]}")
            print("   " + "-" * 50)

            trans.commit()

            print("\n" + "=" * 60)
            print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print("\n📋 Summary:")
            print("   • All data deleted")
            print("   • Old esg_certification (boolean) → Removed")
            print("   • New esg_certification_count (integer) → Added")
            print("   • New esg_certification (text) → Added")
            print("\n📌 Next Steps:")
            print("   1. Restart your backend server")
            print("   2. Test with new chatbot flows")
            print("   3. ESG certifications now stored as text list")
            print()

        except Exception as e:
            trans.rollback()
            print(f"\n❌ Migration failed: {e}")
            raise

if __name__ == "__main__":
    print("\n⚠️  WARNING: This will DELETE ALL DATA in the database!")
    print("   - All chat sessions")
    print("   - All chat messages")
    print("   - All company onboarding data")
    print("   - All products")
    print()

    response = input("Are you sure you want to continue? (yes/no): ")

    if response.lower() == 'yes':
        migrate()
    else:
        print("\n❌ Migration cancelled.")
