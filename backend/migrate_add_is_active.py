"""
Migration script to add is_active column to users table

This script adds the is_active boolean column to the users table
and sets all existing users to active by default.

Usage:
    python migrate_add_is_active.py
"""
import sys
from sqlalchemy import create_engine, text, inspect
from config import get_settings

def run_migration():
    """Run the migration to add is_active column"""
    settings = get_settings()

    print("=" * 60)
    print("Database Migration: Add is_active column to users table")
    print("=" * 60)
    print(f"Database: {settings.database_url[:30]}...")
    print()

    # Create engine
    engine = create_engine(settings.database_url)

    try:
        with engine.connect() as connection:
            # Check if column already exists
            inspector = inspect(engine)
            columns = [col['name'] for col in inspector.get_columns('users')]

            if 'is_active' in columns:
                print("✓ Column 'is_active' already exists in users table")
                print("  No migration needed!")
                return True

            print("Adding 'is_active' column to users table...")

            # Add the column
            connection.execute(text(
                "ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE NOT NULL"
            ))
            connection.commit()

            print("✓ Successfully added 'is_active' column")

            # Update existing users to be active
            result = connection.execute(text(
                "UPDATE users SET is_active = TRUE WHERE is_active IS NULL"
            ))
            connection.commit()

            print(f"✓ Updated existing users (rows affected: {result.rowcount})")

            # Verify the migration
            columns = [col['name'] for col in inspector.get_columns('users')]
            if 'is_active' in columns:
                print("✓ Migration verified successfully!")
                print()
                print("=" * 60)
                print("Migration completed! You can now restart your server.")
                print("=" * 60)
                return True
            else:
                print("✗ Migration verification failed")
                return False

    except Exception as e:
        print(f"✗ Migration failed: {e}")
        print()
        print("Error details:")
        print(f"  {type(e).__name__}: {str(e)}")
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
