-- Migration: Add is_active column to users table
-- Date: 2026-01-08
-- Description: Adds is_active boolean field to users table with default value of TRUE

-- Add the is_active column if it doesn't exist
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE NOT NULL;

-- Update existing users to be active by default
UPDATE users SET is_active = TRUE WHERE is_active IS NULL;

-- Verify the migration
-- SELECT id, username, email, is_active FROM users;
