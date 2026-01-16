"""
Migration script to add is_current field to company_onboarding table
and set the most recent record for each user as current
"""

from sqlalchemy import create_engine, text
from config import get_settings

settings = get_settings()

def migrate():
    """Add is_current column and set the most recent record per user as current"""
    engine = create_engine(settings.database_url)

    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()

        try:
            print("Adding is_current column...")
            # Add is_current column (default False for existing records)
            conn.execute(text("""
                ALTER TABLE company_onboarding
                ADD COLUMN IF NOT EXISTS is_current BOOLEAN DEFAULT FALSE NOT NULL
            """))

            print("Creating index on is_current...")
            # Add index for better performance
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_company_onboarding_is_current
                ON company_onboarding(is_current)
            """))

            print("Setting most recent record per user as current...")
            # Set the most recent record per user as current
            conn.execute(text("""
                UPDATE company_onboarding co1
                SET is_current = TRUE
                WHERE co1.id IN (
                    SELECT DISTINCT ON (user_id) id
                    FROM company_onboarding
                    ORDER BY user_id, created_at DESC
                )
            """))

            # Verify the update
            result = conn.execute(text("""
                SELECT user_id, COUNT(*) as total,
                       SUM(CASE WHEN is_current THEN 1 ELSE 0 END) as current_count
                FROM company_onboarding
                GROUP BY user_id
            """))

            print("\nMigration Results:")
            print("User ID | Total Records | Current Records")
            print("-" * 45)
            for row in result:
                print(f"{row[0]:7d} | {row[1]:13d} | {row[2]:15d}")

            trans.commit()
            print("\n✅ Migration completed successfully!")

        except Exception as e:
            trans.rollback()
            print(f"\n❌ Migration failed: {e}")
            raise

if __name__ == "__main__":
    migrate()
