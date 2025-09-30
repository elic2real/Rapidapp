use std::fs::OpenOptions;
use std::io::Write;
use serde_json::json;
use chrono::Utc;
use crate::error::AppError;

pub struct ErrorCapture;

impl ErrorCapture {
    pub async fn log_error(
        error: &AppError,
        context: &str,
        service: &str,
        additional_data: Option<serde_json::Value>,
    ) {
        let error_log = json!({
            "timestamp": Utc::now().to_rfc3339(),
            "service": service,
            "context": context,
            "error_type": error.error_type(),
            "error_message": error.to_string(),
            "severity": error.severity(),
            "stack_trace": error.stack_trace(),
            "additional_data": additional_data,
            "environment": std::env::var("ENVIRONMENT").unwrap_or_else(|_| "development".to_string()),
            "version": env!("CARGO_PKG_VERSION"),
        });

        // Log to structured error file
        let log_path = "../../logs/errors/event-store-errors.jsonl";
        if let Err(e) = Self::write_error_log(&error_log, log_path).await {
            eprintln!("Failed to write error log: {}", e);
        }

        // Send to error monitoring system
        if let Err(e) = Self::send_to_monitor(&error_log).await {
            eprintln!("Failed to send error to monitor: {}", e);
        }

        // Update error guide if this is a new error pattern
        if let Err(e) = Self::update_error_guide(&error_log).await {
            eprintln!("Failed to update error guide: {}", e);
        }
    }

    async fn write_error_log(
        error_log: &serde_json::Value,
        log_path: &str,
    ) -> Result<(), Box<dyn std::error::Error>> {
        // Ensure log directory exists
        if let Some(parent) = std::path::Path::new(log_path).parent() {
            tokio::fs::create_dir_all(parent).await?;
        }

        let mut file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(log_path)?;

        writeln!(file, "{}", serde_json::to_string(error_log)?)?;
        Ok(())
    }

    async fn send_to_monitor(
        error_log: &serde_json::Value,
    ) -> Result<(), Box<dyn std::error::Error>> {
        let client = reqwest::Client::new();
        
        // Send to local error monitor
        let monitor_url = "http://localhost:8090/errors";
        
        match client
            .post(monitor_url)
            .json(error_log)
            .timeout(Duration::from_secs(5))
            .send()
            .await
        {
            Ok(_) => Ok(()),
            Err(e) => {
                // Don't fail the main operation if monitoring fails
                eprintln!("Warning: Failed to send error to monitor: {}", e);
                Ok(())
            }
        }
    }

    async fn update_error_guide(
        error_log: &serde_json::Value,
    ) -> Result<(), Box<dyn std::error::Error>> {
        // Check if this error pattern exists in our knowledge base
        let error_type = error_log["error_type"].as_str().unwrap_or("unknown");
        let error_message = error_log["error_message"].as_str().unwrap_or("unknown");
        
        // Create error pattern hash for deduplication
        let pattern_hash = format!("{:x}", 
            std::collections::hash_map::DefaultHasher::new()
                .chain(error_type)
                .chain(error_message)
                .finish()
        );

        let new_error_entry = json!({
            "pattern_hash": pattern_hash,
            "error_type": error_type,
            "service": error_log["service"],
            "context": error_log["context"],
            "message": error_message,
            "first_seen": error_log["timestamp"],
            "last_seen": error_log["timestamp"],
            "occurrence_count": 1,
            "resolved": false,
            "solution": null,
            "prevention_tips": [],
            "related_errors": [],
            "severity": error_log["severity"]
        });

        // Write to pending errors file for review and integration
        let pending_path = "../../logs/errors/pending-error-patterns.jsonl";
        if let Some(parent) = std::path::Path::new(pending_path).parent() {
            tokio::fs::create_dir_all(parent).await?;
        }

        let mut file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(pending_path)?;

        writeln!(file, "{}", serde_json::to_string(&new_error_entry)?)?;
        Ok(())
    }
}

use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};
use std::time::Duration;

trait HashBuilder {
    fn chain<T: Hash>(self, value: T) -> Self;
    fn finish(self) -> u64;
}

impl HashBuilder for DefaultHasher {
    fn chain<T: Hash>(mut self, value: T) -> Self {
        value.hash(&mut self);
        self
    }

    fn finish(self) -> u64 {
        Hasher::finish(&self)
    }
}
