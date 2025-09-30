use prometheus::{Counter, Histogram, IntCounter, Registry};
use std::sync::Arc;

#[derive(Clone)]
pub struct Metrics {
    pub registry: Registry,
    pub event_append_requests: IntCounter,
    pub event_append_errors: IntCounter,
    pub event_append_conflicts: IntCounter,
    pub event_append_duration: Histogram,
    pub event_read_requests: IntCounter,
    pub event_read_errors: IntCounter,
    pub event_read_duration: Histogram,
    pub events_stored: IntCounter,
    pub events_read: IntCounter,
    pub snapshot_create_requests: IntCounter,
    pub snapshot_create_errors: IntCounter,
    pub snapshot_create_duration: Histogram,
    pub snapshot_read_requests: IntCounter,
    pub snapshot_read_errors: IntCounter,
    pub snapshot_read_duration: Histogram,
    pub snapshots_created: IntCounter,
    pub snapshots_read: IntCounter,
}

impl Metrics {
    pub fn new() -> Self {
        let registry = Registry::new();

        let event_append_requests = IntCounter::new(
            "event_store_append_requests_total",
            "Total number of event append requests"
        ).expect("Failed to create metric");

        let event_append_errors = IntCounter::new(
            "event_store_append_errors_total",
            "Total number of event append errors"
        ).expect("Failed to create metric");

        let event_append_conflicts = IntCounter::new(
            "event_store_append_conflicts_total",
            "Total number of event append conflicts"
        ).expect("Failed to create metric");

        let event_append_duration = Histogram::new(
            prometheus::HistogramOpts::new(
                "event_store_append_duration_seconds",
                "Duration of event append operations"
            ).buckets(vec![0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0])
        ).expect("Failed to create metric");

        let event_read_requests = IntCounter::new(
            "event_store_read_requests_total",
            "Total number of event read requests"
        ).expect("Failed to create metric");

        let event_read_errors = IntCounter::new(
            "event_store_read_errors_total",
            "Total number of event read errors"
        ).expect("Failed to create metric");

        let event_read_duration = Histogram::new(
            prometheus::HistogramOpts::new(
                "event_store_read_duration_seconds",
                "Duration of event read operations"
            ).buckets(vec![0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0])
        ).expect("Failed to create metric");

        let events_stored = IntCounter::new(
            "event_store_events_stored_total",
            "Total number of events stored"
        ).expect("Failed to create metric");

        let events_read = IntCounter::new(
            "event_store_events_read_total",
            "Total number of events read"
        ).expect("Failed to create metric");

        let snapshot_create_requests = IntCounter::new(
            "event_store_snapshot_create_requests_total",
            "Total number of snapshot create requests"
        ).expect("Failed to create metric");

        let snapshot_create_errors = IntCounter::new(
            "event_store_snapshot_create_errors_total",
            "Total number of snapshot create errors"
        ).expect("Failed to create metric");

        let snapshot_create_duration = Histogram::new(
            prometheus::HistogramOpts::new(
                "event_store_snapshot_create_duration_seconds",
                "Duration of snapshot create operations"
            ).buckets(vec![0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0])
        ).expect("Failed to create metric");

        let snapshot_read_requests = IntCounter::new(
            "event_store_snapshot_read_requests_total",
            "Total number of snapshot read requests"
        ).expect("Failed to create metric");

        let snapshot_read_errors = IntCounter::new(
            "event_store_snapshot_read_errors_total",
            "Total number of snapshot read errors"
        ).expect("Failed to create metric");

        let snapshot_read_duration = Histogram::new(
            prometheus::HistogramOpts::new(
                "event_store_snapshot_read_duration_seconds",
                "Duration of snapshot read operations"
            ).buckets(vec![0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0])
        ).expect("Failed to create metric");

        let snapshots_created = IntCounter::new(
            "event_store_snapshots_created_total",
            "Total number of snapshots created"
        ).expect("Failed to create metric");

        let snapshots_read = IntCounter::new(
            "event_store_snapshots_read_total",
            "Total number of snapshots read"
        ).expect("Failed to create metric");

        // Register all metrics
        registry.register(Box::new(event_append_requests.clone())).expect("Failed to register metric");
        registry.register(Box::new(event_append_errors.clone())).expect("Failed to register metric");
        registry.register(Box::new(event_append_conflicts.clone())).expect("Failed to register metric");
        registry.register(Box::new(event_append_duration.clone())).expect("Failed to register metric");
        registry.register(Box::new(event_read_requests.clone())).expect("Failed to register metric");
        registry.register(Box::new(event_read_errors.clone())).expect("Failed to register metric");
        registry.register(Box::new(event_read_duration.clone())).expect("Failed to register metric");
        registry.register(Box::new(events_stored.clone())).expect("Failed to register metric");
        registry.register(Box::new(events_read.clone())).expect("Failed to register metric");
        registry.register(Box::new(snapshot_create_requests.clone())).expect("Failed to register metric");
        registry.register(Box::new(snapshot_create_errors.clone())).expect("Failed to register metric");
        registry.register(Box::new(snapshot_create_duration.clone())).expect("Failed to register metric");
        registry.register(Box::new(snapshot_read_requests.clone())).expect("Failed to register metric");
        registry.register(Box::new(snapshot_read_errors.clone())).expect("Failed to register metric");
        registry.register(Box::new(snapshot_read_duration.clone())).expect("Failed to register metric");
        registry.register(Box::new(snapshots_created.clone())).expect("Failed to register metric");
        registry.register(Box::new(snapshots_read.clone())).expect("Failed to register metric");

        Self {
            registry,
            event_append_requests,
            event_append_errors,
            event_append_conflicts,
            event_append_duration,
            event_read_requests,
            event_read_errors,
            event_read_duration,
            events_stored,
            events_read,
            snapshot_create_requests,
            snapshot_create_errors,
            snapshot_create_duration,
            snapshot_read_requests,
            snapshot_read_errors,
            snapshot_read_duration,
            snapshots_created,
            snapshots_read,
        }
    }
}
