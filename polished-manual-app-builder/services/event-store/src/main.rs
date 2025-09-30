use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    response::Json,
    routing::{get, post},
    Router,
};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::{PgPool, Row};
use std::{collections::HashMap, sync::Arc, time::Duration};
use tokio::time::sleep;
use tower::ServiceBuilder;
use tower_http::{compression::CompressionLayer, cors::CorsLayer, trace::TraceLayer};
use tracing::{error, info, warn};
use uuid::Uuid;

mod config;
mod error;
mod error_capture;
mod metrics;
mod telemetry;

use config::Config;
use error::{AppError, Result};
use error_capture::ErrorCapture;
use metrics::Metrics;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Event {
    pub id: Uuid,
    pub stream_id: String,
    pub event_type: String,
    pub data: serde_json::Value,
    pub metadata: Option<serde_json::Value>,
    pub version: i64,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct AppendEventRequest {
    pub stream_id: String,
    pub event_type: String,
    pub data: serde_json::Value,
    pub metadata: Option<serde_json::Value>,
    pub expected_version: Option<i64>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct EventsQuery {
    pub from_version: Option<i64>,
    pub limit: Option<i64>,
    pub direction: Option<String>, // "forward" or "backward"
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Snapshot {
    pub id: Uuid,
    pub stream_id: String,
    pub version: i64,
    pub data: Vec<u8>, // Compressed data
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CreateSnapshotRequest {
    pub stream_id: String,
    pub version: i64,
    pub data: serde_json::Value,
}

#[derive(Debug, Clone)]
pub struct AppState {
    pub db: PgPool,
    pub config: Config,
    pub metrics: Metrics,
}

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize tracing
    telemetry::init()?;

    // Load configuration
    let config = Config::load()?;

    // Initialize database
    let db = initialize_database(&config.database_url).await?;
    run_migrations(&db).await?;

    // Initialize metrics
    let metrics = Metrics::new();

    let state = AppState {
        db: db.clone(),
        config: config.clone(),
        metrics: metrics.clone(),
    };

    // Start background tasks
    tokio::spawn(snapshot_scheduler(db.clone(), config.clone()));
    tokio::spawn(stream_archiver(db.clone(), config.clone()));

    // Build application
    let app = create_app(state);

    // Start server
    let listener = tokio::net::TcpListener::bind(&config.server_address).await?;
    info!("Event Store server starting on {}", config.server_address);

    axum::serve(listener, app).await?;

    Ok(())
}

fn create_app(state: AppState) -> Router {
    Router::new()
        .route("/health", get(health_check))
        .route("/metrics", get(get_metrics))
        .route("/events", post(append_event))
        .route("/streams/:stream_id/events", get(get_stream_events))
        .route("/snapshots", post(create_snapshot))
        .route("/snapshots/:stream_id/latest", get(get_latest_snapshot))
        .route("/stats", get(get_stats))
        .with_state(state)
        .layer(
            ServiceBuilder::new()
                .layer(TraceLayer::new_for_http())
                .layer(CompressionLayer::new())
                .layer(CorsLayer::permissive())
        )
}

async fn health_check() -> Result<Json<serde_json::Value>> {
    Ok(Json(serde_json::json!({
        "status": "healthy",
        "service": "event-store",
        "version": "1.0.0",
        "timestamp": Utc::now()
    })))
}

async fn get_metrics(State(state): State<AppState>) -> Result<String> {
    let encoder = prometheus::TextEncoder::new();
    let metric_families = state.metrics.registry.gather();
    match encoder.encode_to_string(&metric_families) {
        Ok(metrics) => Ok(metrics),
        Err(e) => {
            error!("Failed to encode metrics: {}", e);
            Err(AppError::Internal("Failed to encode metrics".to_string()))
        }
    }
}

async fn append_event(
    State(state): State<AppState>,
    Json(request): Json<AppendEventRequest>,
) -> Result<Json<Event>> {
    let start_time = std::time::Instant::now();
    state.metrics.event_append_requests.inc();

    // Validate stream_id format for partitioning
    if !is_valid_stream_id(&request.stream_id) {
        state.metrics.event_append_errors.inc();
        return Err(AppError::BadRequest("Invalid stream_id format".to_string()));
    }

    // Get current version for optimistic concurrency control
    let current_version = get_stream_version(&state.db, &request.stream_id).await?;

    if let Some(expected) = request.expected_version {
        if current_version != expected {
            state.metrics.event_append_conflicts.inc();
            return Err(AppError::Conflict(format!(
                "Version conflict: expected {}, got {}",
                expected, current_version
            )));
        }
    }

    let new_version = current_version + 1;
    let event_id = Uuid::new_v4();
    let now = Utc::now();

    // Insert event with partition key
    let partition_key = get_partition_key(&request.stream_id);

    sqlx::query!(
        r#"
        INSERT INTO events (id, stream_id, event_type, data, metadata, version, created_at, partition_key)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        "#,
        event_id,
        request.stream_id,
        request.event_type,
        request.data,
        request.metadata,
        new_version,
        now,
        partition_key
    )
    .execute(&state.db)
    .await
    .map_err(|e| {
        error!("Failed to insert event: {}", e);
        state.metrics.event_append_errors.inc();
        AppError::Database(e.to_string())
    })?;

    let event = Event {
        id: event_id,
        stream_id: request.stream_id,
        event_type: request.event_type,
        data: request.data,
        metadata: request.metadata,
        version: new_version,
        created_at: now,
    };

    state.metrics.events_stored.inc();
    state.metrics.event_append_duration.observe(start_time.elapsed().as_secs_f64());

    info!("Event appended: {} v{}", event.stream_id, event.version);

    Ok(Json(event))
}

async fn get_stream_events(
    Path(stream_id): Path<String>,
    Query(query): Query<EventsQuery>,
    State(state): State<AppState>,
) -> Result<Json<Vec<Event>>> {
    let start_time = std::time::Instant::now();
    state.metrics.event_read_requests.inc();

    let from_version = query.from_version.unwrap_or(0);
    let limit = query.limit.unwrap_or(100).min(1000); // Cap at 1000
    let direction = query.direction.unwrap_or_else(|| "forward".to_string());

    let order_clause = if direction == "backward" { "DESC" } else { "ASC" };

    let query_str = format!(
        r#"
        SELECT id, stream_id, event_type, data, metadata, version, created_at
        FROM events
        WHERE stream_id = $1 AND version >= $2
        ORDER BY version {}
        LIMIT $3
        "#,
        order_clause
    );

    let rows = sqlx::query(&query_str)
        .bind(&stream_id)
        .bind(from_version)
        .bind(limit)
        .fetch_all(&state.db)
        .await
        .map_err(|e| {
            error!("Failed to fetch events: {}", e);
            state.metrics.event_read_errors.inc();
            AppError::Database(e.to_string())
        })?;

    let events: Result<Vec<Event>> = rows
        .into_iter()
        .map(|row| {
            Ok(Event {
                id: row.try_get("id")?,
                stream_id: row.try_get("stream_id")?,
                event_type: row.try_get("event_type")?,
                data: row.try_get("data")?,
                metadata: row.try_get("metadata")?,
                version: row.try_get("version")?,
                created_at: row.try_get("created_at")?,
            })
        })
        .collect();

    let events = events?;
    state.metrics.events_read.inc_by(events.len() as u64);
    state.metrics.event_read_duration.observe(start_time.elapsed().as_secs_f64());

    Ok(Json(events))
}

async fn create_snapshot(
    State(state): State<AppState>,
    Json(request): Json<CreateSnapshotRequest>,
) -> Result<Json<Snapshot>> {
    let start_time = std::time::Instant::now();
    state.metrics.snapshot_create_requests.inc();

    // Compress data
    let serialized_data = serde_json::to_vec(&request.data).map_err(|e| {
        error!("Failed to serialize snapshot data: {}", e);
        AppError::Internal("Serialization failed".to_string())
    })?;

    let compressed_data = lz4_flex::compress(&serialized_data);

    let snapshot_id = Uuid::new_v4();
    let now = Utc::now();

    // Delete old snapshots for this stream (keep only latest)
    sqlx::query!(
        "DELETE FROM snapshots WHERE stream_id = $1",
        request.stream_id
    )
    .execute(&state.db)
    .await
    .map_err(|e| {
        error!("Failed to delete old snapshots: {}", e);
        AppError::Database(e.to_string())
    })?;

    // Insert new snapshot
    sqlx::query!(
        r#"
        INSERT INTO snapshots (id, stream_id, version, data, created_at)
        VALUES ($1, $2, $3, $4, $5)
        "#,
        snapshot_id,
        request.stream_id,
        request.version,
        compressed_data,
        now
    )
    .execute(&state.db)
    .await
    .map_err(|e| {
        error!("Failed to insert snapshot: {}", e);
        state.metrics.snapshot_create_errors.inc();
        AppError::Database(e.to_string())
    })?;

    let snapshot = Snapshot {
        id: snapshot_id,
        stream_id: request.stream_id,
        version: request.version,
        data: compressed_data,
        created_at: now,
    };

    state.metrics.snapshots_created.inc();
    state.metrics.snapshot_create_duration.observe(start_time.elapsed().as_secs_f64());

    info!("Snapshot created: {} v{}", snapshot.stream_id, snapshot.version);

    Ok(Json(snapshot))
}

async fn get_latest_snapshot(
    Path(stream_id): Path<String>,
    State(state): State<AppState>,
) -> Result<Json<Option<serde_json::Value>>> {
    let start_time = std::time::Instant::now();
    state.metrics.snapshot_read_requests.inc();

    let row = sqlx::query!(
        "SELECT data FROM snapshots WHERE stream_id = $1 ORDER BY version DESC LIMIT 1",
        stream_id
    )
    .fetch_optional(&state.db)
    .await
    .map_err(|e| {
        error!("Failed to fetch snapshot: {}", e);
        state.metrics.snapshot_read_errors.inc();
        AppError::Database(e.to_string())
    })?;

    let result = if let Some(row) = row {
        // Decompress data
        let decompressed = lz4_flex::decompress(&row.data, 1024 * 1024) // 1MB max
            .map_err(|e| {
                error!("Failed to decompress snapshot: {}", e);
                AppError::Internal("Decompression failed".to_string())
            })?;

        let data: serde_json::Value = serde_json::from_slice(&decompressed)
            .map_err(|e| {
                error!("Failed to deserialize snapshot: {}", e);
                AppError::Internal("Deserialization failed".to_string())
            })?;

        Some(data)
    } else {
        None
    };

    state.metrics.snapshots_read.inc();
    state.metrics.snapshot_read_duration.observe(start_time.elapsed().as_secs_f64());

    Ok(Json(result))
}

async fn get_stats(State(state): State<AppState>) -> Result<Json<serde_json::Value>> {
    let total_events: i64 = sqlx::query_scalar!("SELECT COUNT(*) FROM events")
        .fetch_one(&state.db)
        .await
        .map_err(|e| AppError::Database(e.to_string()))?
        .unwrap_or(0);

    let total_streams: i64 = sqlx::query_scalar!("SELECT COUNT(DISTINCT stream_id) FROM events")
        .fetch_one(&state.db)
        .await
        .map_err(|e| AppError::Database(e.to_string()))?
        .unwrap_or(0);

    let total_snapshots: i64 = sqlx::query_scalar!("SELECT COUNT(*) FROM snapshots")
        .fetch_one(&state.db)
        .await
        .map_err(|e| AppError::Database(e.to_string()))?
        .unwrap_or(0);

    Ok(Json(serde_json::json!({
        "total_events": total_events,
        "total_streams": total_streams,
        "total_snapshots": total_snapshots,
        "uptime_seconds": std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs()
    })))
}

async fn initialize_database(database_url: &str) -> Result<PgPool> {
    info!("Connecting to database...");
    
    let pool = PgPool::connect(database_url)
        .await
        .map_err(|e| AppError::Database(format!("Failed to connect to database: {}", e)))?;

    info!("Database connection established");
    Ok(pool)
}

async fn run_migrations(pool: &PgPool) -> Result<()> {
    info!("Running database migrations...");

    // Create events table
    sqlx::query!(
        r#"
        CREATE TABLE IF NOT EXISTS events (
            id UUID PRIMARY KEY,
            stream_id VARCHAR NOT NULL,
            event_type VARCHAR NOT NULL,
            data JSONB NOT NULL,
            metadata JSONB,
            version BIGINT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            partition_key VARCHAR NOT NULL,
            UNIQUE(stream_id, version)
        )
        "#
    )
    .execute(pool)
    .await
    .map_err(|e| AppError::Database(format!("Failed to create events table: {}", e)))?;

    // Create indexes for performance
    sqlx::query!("CREATE INDEX IF NOT EXISTS idx_events_stream_version ON events(stream_id, version)")
        .execute(pool)
        .await
        .map_err(|e| AppError::Database(format!("Failed to create stream_version index: {}", e)))?;

    sqlx::query!("CREATE INDEX IF NOT EXISTS idx_events_partition_key ON events(partition_key)")
        .execute(pool)
        .await
        .map_err(|e| AppError::Database(format!("Failed to create partition_key index: {}", e)))?;

    sqlx::query!("CREATE INDEX IF NOT EXISTS idx_events_created_at ON events(created_at)")
        .execute(pool)
        .await
        .map_err(|e| AppError::Database(format!("Failed to create created_at index: {}", e)))?;

    // Create snapshots table
    sqlx::query!(
        r#"
        CREATE TABLE IF NOT EXISTS snapshots (
            id UUID PRIMARY KEY,
            stream_id VARCHAR NOT NULL,
            version BIGINT NOT NULL,
            data BYTEA NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE(stream_id, version)
        )
        "#
    )
    .execute(pool)
    .await
    .map_err(|e| AppError::Database(format!("Failed to create snapshots table: {}", e)))?;

    sqlx::query!("CREATE INDEX IF NOT EXISTS idx_snapshots_stream_version ON snapshots(stream_id, version DESC)")
        .execute(pool)
        .await
        .map_err(|e| AppError::Database(format!("Failed to create snapshots index: {}", e)))?;

    info!("Database migrations completed");
    Ok(())
}

async fn get_stream_version(pool: &PgPool, stream_id: &str) -> Result<i64> {
    let version: Option<i64> = sqlx::query_scalar!(
        "SELECT MAX(version) FROM events WHERE stream_id = $1",
        stream_id
    )
    .fetch_one(pool)
    .await
    .map_err(|e| AppError::Database(e.to_string()))?;

    Ok(version.unwrap_or(0))
}

fn is_valid_stream_id(stream_id: &str) -> bool {
    // Stream ID format: {project_id}/{workspace_id}/{stream_name}
    stream_id.len() <= 255 && stream_id.chars().all(|c| c.is_alphanumeric() || c == '-' || c == '_' || c == '/')
}

fn get_partition_key(stream_id: &str) -> String {
    // Use project_id (first part) as partition key
    stream_id.split('/').next().unwrap_or(stream_id).to_string()
}

// Background task: Create snapshots periodically
async fn snapshot_scheduler(pool: PgPool, config: Config) {
    let mut interval = tokio::time::interval(Duration::from_secs(config.snapshot_interval_seconds));
    
    loop {
        interval.tick().await;
        
        info!("Running scheduled snapshot creation...");
        
        // Find streams that need snapshots (version > last_snapshot_version + threshold)
        let streams = match sqlx::query!(
            r#"
            SELECT e.stream_id, MAX(e.version) as current_version,
                   COALESCE(s.version, 0) as snapshot_version
            FROM events e
            LEFT JOIN snapshots s ON e.stream_id = s.stream_id
            GROUP BY e.stream_id, s.version
            HAVING MAX(e.version) - COALESCE(s.version, 0) >= $1
            "#,
            config.snapshot_threshold
        )
        .fetch_all(&pool)
        .await
        {
            Ok(streams) => streams,
            Err(e) => {
                error!("Failed to query streams for snapshots: {}", e);
                continue;
            }
        };

        for stream in streams {
            let stream_id = &stream.stream_id;
            let version = stream.current_version;

            // Rebuild state from events to create snapshot
            match rebuild_stream_state(&pool, stream_id, version).await {
                Ok(state_data) => {
                    let compressed_data = match serde_json::to_vec(&state_data)
                        .and_then(|data| Ok(lz4_flex::compress(&data)))
                    {
                        Ok(data) => data,
                        Err(e) => {
                            error!("Failed to compress snapshot data for {}: {}", stream_id, e);
                            continue;
                        }
                    };

                    if let Err(e) = sqlx::query!(
                        r#"
                        INSERT INTO snapshots (id, stream_id, version, data, created_at)
                        VALUES ($1, $2, $3, $4, NOW())
                        ON CONFLICT (stream_id, version) DO NOTHING
                        "#,
                        Uuid::new_v4(),
                        stream_id,
                        version,
                        compressed_data
                    )
                    .execute(&pool)
                    .await
                    {
                        error!("Failed to create snapshot for {}: {}", stream_id, e);
                    } else {
                        info!("Created snapshot for {} at version {}", stream_id, version);
                    }
                }
                Err(e) => {
                    error!("Failed to rebuild state for {}: {}", stream_id, e);
                }
            }
        }

        info!("Scheduled snapshot creation completed");
    }
}

// Background task: Archive old streams
async fn stream_archiver(pool: PgPool, config: Config) {
    let mut interval = tokio::time::interval(Duration::from_secs(config.archive_interval_seconds));
    
    loop {
        interval.tick().await;
        
        info!("Running stream archival...");
        
        // Archive streams older than threshold that have snapshots
        let archive_threshold = Utc::now() - chrono::Duration::days(config.archive_days);
        
        match sqlx::query!(
            r#"
            UPDATE events 
            SET archived = true 
            WHERE created_at < $1 
            AND stream_id IN (SELECT stream_id FROM snapshots)
            AND archived = false
            "#,
            archive_threshold
        )
        .execute(&pool)
        .await
        {
            Ok(result) => {
                info!("Archived {} events", result.rows_affected());
            }
            Err(e) => {
                error!("Failed to archive events: {}", e);
            }
        }

        sleep(Duration::from_secs(1)).await;
    }
}

async fn rebuild_stream_state(
    pool: &PgPool,
    stream_id: &str,
    up_to_version: i64,
) -> Result<serde_json::Value> {
    let events = sqlx::query!(
        "SELECT data FROM events WHERE stream_id = $1 AND version <= $2 ORDER BY version",
        stream_id,
        up_to_version
    )
    .fetch_all(pool)
    .await
    .map_err(|e| AppError::Database(e.to_string()))?;

    // Simple state reconstruction - just collect all event data
    let state: Vec<serde_json::Value> = events.into_iter().map(|row| row.data).collect();
    
    Ok(serde_json::json!({
        "events": state,
        "version": up_to_version,
        "reconstructed_at": Utc::now()
    }))
}
