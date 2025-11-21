-- Add OAuth support to users table
-- This migration adds fields and policies to support OAuth authentication

-- Add OAuth provider field if it doesn't exist
DO $$ 
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'users' AND column_name = 'oauth_provider'
  ) THEN
    ALTER TABLE users ADD COLUMN oauth_provider VARCHAR(50);
  END IF;
END $$;

-- Add OAuth provider user ID field if it doesn't exist
DO $$ 
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'users' AND column_name = 'oauth_provider_id'
  ) THEN
    ALTER TABLE users ADD COLUMN oauth_provider_id VARCHAR(255);
  END IF;
END $$;

-- Add avatar URL field for OAuth profile pictures
DO $$ 
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'users' AND column_name = 'avatar_url'
  ) THEN
    ALTER TABLE users ADD COLUMN avatar_url TEXT;
  END IF;
END $$;

-- Make password_hash nullable for OAuth users
ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL;

-- Add comment to explain nullable password
COMMENT ON COLUMN users.password_hash IS 'Password hash for email/password auth. NULL for OAuth-only users.';

-- Create index on oauth_provider_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_oauth_provider_id ON users(oauth_provider_id);

-- Update RLS policies to allow OAuth user creation
-- Drop existing policy if it exists
DROP POLICY IF EXISTS "Users can insert their own profile during signup" ON users;

-- Create new policy that allows inserts during auth
CREATE POLICY "Users can insert their own profile during signup"
ON users FOR INSERT
WITH CHECK (
  auth.uid() = id
);

-- Allow users to read their own profile
DROP POLICY IF EXISTS "Users can read their own profile" ON users;
CREATE POLICY "Users can read their own profile"
ON users FOR SELECT
USING (auth.uid() = id);

-- Allow users to update their own profile
DROP POLICY IF EXISTS "Users can update their own profile" ON users;
CREATE POLICY "Users can update their own profile"
ON users FOR UPDATE
USING (auth.uid() = id)
WITH CHECK (auth.uid() = id);

-- Create a function to handle OAuth user creation
CREATE OR REPLACE FUNCTION handle_oauth_user()
RETURNS TRIGGER AS $$
BEGIN
  -- If this is an OAuth user (has oauth_provider), ensure they're verified
  IF NEW.oauth_provider IS NOT NULL THEN
    NEW.is_verified := TRUE;
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger for OAuth user creation
DROP TRIGGER IF EXISTS on_oauth_user_created ON users;
CREATE TRIGGER on_oauth_user_created
  BEFORE INSERT ON users
  FOR EACH ROW
  EXECUTE FUNCTION handle_oauth_user();

-- Add helpful comments
COMMENT ON COLUMN users.oauth_provider IS 'OAuth provider name (google, github, etc.)';
COMMENT ON COLUMN users.oauth_provider_id IS 'User ID from the OAuth provider';
COMMENT ON COLUMN users.avatar_url IS 'Profile picture URL from OAuth provider or uploaded';

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON users TO authenticated;
GRANT SELECT ON users TO anon;
