-- Create databases for different services
CREATE DATABASE IF NOT EXISTS event_store;
CREATE DATABASE IF NOT EXISTS orchestrator_cache;
CREATE DATABASE IF NOT EXISTS feature_flags;
CREATE DATABASE IF NOT EXISTS validation_pipeline;

-- Create users
CREATE USER IF NOT EXISTS 'event_store_user'@'%' IDENTIFIED BY 'event_store_pass';
CREATE USER IF NOT EXISTS 'orchestrator_user'@'%' IDENTIFIED BY 'orchestrator_pass';
CREATE USER IF NOT EXISTS 'feature_flags_user'@'%' IDENTIFIED BY 'feature_flags_pass';
CREATE USER IF NOT EXISTS 'validation_user'@'%' IDENTIFIED BY 'validation_pass';

-- Grant permissions
GRANT ALL PRIVILEGES ON event_store.* TO 'event_store_user'@'%';
GRANT ALL PRIVILEGES ON orchestrator_cache.* TO 'orchestrator_user'@'%';
GRANT ALL PRIVILEGES ON feature_flags.* TO 'feature_flags_user'@'%';
GRANT ALL PRIVILEGES ON validation_pipeline.* TO 'validation_user'@'%';

FLUSH PRIVILEGES;
