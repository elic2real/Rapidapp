use axum::{
    http::StatusCode,
    response::{IntoResponse, Response},
    Json,
};
use serde_json::json;
use thiserror::Error;

pub type Result<T> = std::result::Result<T, AppError>;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("Database error: {0}")]
    Database(String),

    #[error("Bad request: {0}")]
    BadRequest(String),

    #[error("Conflict: {0}")]
    Conflict(String),

    #[error("Not found: {0}")]
    NotFound(String),

    #[error("Internal error: {0}")]
    Internal(String),

    #[error("Serialization error: {0}")]
    Serialization(#[from] serde_json::Error),

    #[error("SQL error: {0}")]
    Sql(#[from] sqlx::Error),
}

impl AppError {
    pub fn error_type(&self) -> &str {
        match self {
            AppError::Database(_) => "DATABASE_ERROR",
            AppError::BadRequest(_) => "BAD_REQUEST",
            AppError::Conflict(_) => "CONFLICT",
            AppError::NotFound(_) => "NOT_FOUND",
            AppError::Internal(_) => "INTERNAL_ERROR",
            AppError::Serialization(_) => "SERIALIZATION_ERROR",
            AppError::Sql(_) => "SQL_ERROR",
        }
    }

    pub fn severity(&self) -> &str {
        match self {
            AppError::Database(_) | AppError::Sql(_) => "high",
            AppError::Internal(_) => "critical",
            AppError::BadRequest(_) | AppError::Serialization(_) => "low",
            AppError::Conflict(_) | AppError::NotFound(_) => "medium",
        }
    }

    pub fn stack_trace(&self) -> Option<String> {
        // In a real implementation, you'd capture the actual stack trace
        Some(format!("Error occurred in event-store service: {}", self))
    }
}

impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        let (status, error_message) = match &self {
            AppError::Database(_) => (StatusCode::INTERNAL_SERVER_ERROR, "Database error"),
            AppError::BadRequest(_) => (StatusCode::BAD_REQUEST, "Bad request"),
            AppError::Conflict(_) => (StatusCode::CONFLICT, "Conflict"),
            AppError::NotFound(_) => (StatusCode::NOT_FOUND, "Not found"),
            AppError::Internal(_) => (StatusCode::INTERNAL_SERVER_ERROR, "Internal error"),
            AppError::Serialization(_) => (StatusCode::BAD_REQUEST, "Serialization error"),
            AppError::Sql(_) => (StatusCode::INTERNAL_SERVER_ERROR, "Database error"),
        };

        let body = Json(json!({
            "error": error_message,
            "message": self.to_string(),
        }));

        (status, body).into_response()
    }
}
