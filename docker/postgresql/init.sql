-- Initialize PostgreSQL database for Elevate Team Formation App
-- This script runs when the PostgreSQL container is first created

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create additional databases for testing if needed
-- Commented out for now, can be uncommented if test database is needed
-- CREATE DATABASE elevate_test_db;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE elevate_db TO elevate_user;

-- Create schema for tenant isolation (will be handled by application migrations)
-- This is just a placeholder for any initialization SQL
