"""
Migration: Remove Company Info Fields from CompanyOnboarding
Date: 2026-01-12
Description: Remove fields that are not the chatbot's responsibility:
  - company_id
  - company_name
  - country
  - tax
  - address

These fields are no longer collected by the chatbot API.
"""

def migrate():
    """
    Apply the migration to remove company info fields

    Run this script with:
    python migrations/003_remove_company_info_fields.py
    """
    from sqlalchemy import create_engine, text
    from config import get_settings

    settings = get_settings()
    engine = create_engine(settings.database_url)

    with engine.connect() as connection:
        # Start transaction
        trans = connection.begin()

        try:
            print("Removing company info fields from company_onboarding table...")

            # Drop columns that are no longer needed
            connection.execute(text("""
                ALTER TABLE company_onboarding
                DROP COLUMN IF EXISTS company_id,
                DROP COLUMN IF EXISTS company_name,
                DROP COLUMN IF EXISTS country,
                DROP COLUMN IF EXISTS tax,
                DROP COLUMN IF EXISTS address;
            """))

            print("✓ Successfully removed: company_id, company_name, country, tax, address")

            # Commit transaction
            trans.commit()
            print("✓ Migration completed successfully")

        except Exception as e:
            # Rollback on error
            trans.rollback()
            print(f"✗ Migration failed: {str(e)}")
            raise


def rollback():
    """
    Rollback the migration - restore the removed columns

    WARNING: This will add back the columns but data will be NULL
    """
    from sqlalchemy import create_engine, text
    from config import get_settings

    settings = get_settings()
    engine = create_engine(settings.database_url)

    with engine.connect() as connection:
        trans = connection.begin()

        try:
            print("Rolling back: Adding company info fields back to company_onboarding table...")

            connection.execute(text("""
                ALTER TABLE company_onboarding
                ADD COLUMN IF NOT EXISTS company_id VARCHAR(100),
                ADD COLUMN IF NOT EXISTS company_name VARCHAR(200),
                ADD COLUMN IF NOT EXISTS country VARCHAR(100),
                ADD COLUMN IF NOT EXISTS tax INTEGER,
                ADD COLUMN IF NOT EXISTS address VARCHAR(500);
            """))

            # Recreate index on company_id
            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_company_onboarding_company_id
                ON company_onboarding(company_id);
            """))

            print("✓ Successfully added back: company_id, company_name, country, tax, address")
            print("⚠ WARNING: All values will be NULL. Manual data restoration may be required.")

            trans.commit()
            print("✓ Rollback completed successfully")

        except Exception as e:
            trans.rollback()
            print(f"✗ Rollback failed: {str(e)}")
            raise


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        print("Running rollback...")
        rollback()
    else:
        print("Running migration...")
        migrate()
