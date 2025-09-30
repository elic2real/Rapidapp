-- Create databases for different services (PostgreSQL compatible)
-- Note: PostgreSQL doesn't support CREATE DATABASE IF NOT EXISTS

-- The polished_manual database is already created by default
-- We'll use schemas within the main database instead

-- Create schemas for different services
CREATE SCHEMA IF NOT EXISTS event_store;
CREATE SCHEMA IF NOT EXISTS orchestrator_cache;
CREATE SCHEMA IF NOT EXISTS feature_flags;
CREATE SCHEMA IF NOT EXISTS validation_pipeline;

-- Create users (PostgreSQL syntax)
DO
$do$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'event_store_user') THEN
      CREATE ROLE event_store_user LOGIN PASSWORD 'event_store_pass';
   END IF;
   
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'orchestrator_user') THEN
      CREATE ROLE orchestrator_user LOGIN PASSWORD 'orchestrator_pass';
   END IF;
   
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'feature_flags_user') THEN
      CREATE ROLE feature_flags_user LOGIN PASSWORD 'feature_flags_pass';
   END IF;
   
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'validation_user') THEN
      CREATE ROLE validation_user LOGIN PASSWORD 'validation_pass';
   END IF;
END
$do$;

-- Grant permissions on schemas
GRANT ALL PRIVILEGES ON SCHEMA event_store TO event_store_user;
GRANT ALL PRIVILEGES ON SCHEMA orchestrator_cache TO orchestrator_user;
GRANT ALL PRIVILEGES ON SCHEMA feature_flags TO feature_flags_user;
GRANT ALL PRIVILEGES ON SCHEMA validation_pipeline TO validation_user;
