use serde::Deserialize;
use anyhow::Result;

#[derive(Debug, Clone, Deserialize)]
pub struct Config {
    pub server_address: String,
    pub database_url: String,
    pub snapshot_interval_seconds: u64,
    pub snapshot_threshold: i64,
    pub archive_interval_seconds: u64,
    pub archive_days: i64,
    pub jaeger_endpoint: Option<String>,
}

impl Config {
    pub fn load() -> Result<Self> {
        dotenvy::dotenv().ok();

        let config = Self {
            server_address: std::env::var("SERVER_ADDRESS")
                .unwrap_or_else(|_| "0.0.0.0:8080".to_string()),
            database_url: std::env::var("DATABASE_URL")
                .unwrap_or_else(|_| "postgres://postgres:postgres@localhost:5432/polished_manual".to_string()),
            snapshot_interval_seconds: std::env::var("SNAPSHOT_INTERVAL_SECONDS")
                .unwrap_or_else(|_| "3600".to_string()) // 1 hour
                .parse()?,
            snapshot_threshold: std::env::var("SNAPSHOT_THRESHOLD")
                .unwrap_or_else(|_| "1000".to_string()) // 1000 events
                .parse()?,
            archive_interval_seconds: std::env::var("ARCHIVE_INTERVAL_SECONDS")
                .unwrap_or_else(|_| "86400".to_string()) // 24 hours
                .parse()?,
            archive_days: std::env::var("ARCHIVE_DAYS")
                .unwrap_or_else(|_| "90".to_string()) // 90 days
                .parse()?,
            jaeger_endpoint: std::env::var("JAEGER_ENDPOINT").ok(),
        };

        Ok(config)
    }
}
