-- Initialize CI/CD test database
-- This script runs automatically when PostgreSQL container starts for the first time

-- Create additional test database if needed
-- CREATE DATABASE test_familycart_integration;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE test_familycart TO test_user;

-- Create extensions if needed
\c test_familycart;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Log initialization
\echo 'CI/CD test database initialized successfully'