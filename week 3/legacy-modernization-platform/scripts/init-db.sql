-- Ensure database and privileges are configured cleanly
GRANT ALL PRIVILEGES ON DATABASE legacy_db TO app_user;

-- Create default schema if needed
CREATE SCHEMA IF NOT EXISTS public AUTHORIZATION app_user;
