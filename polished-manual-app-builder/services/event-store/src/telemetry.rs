use anyhow::Result;
use opentelemetry::{trace::TraceError, KeyValue};
use opentelemetry_otlp::WithExportConfig;
use opentelemetry_sdk::{trace, Resource};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt, EnvFilter};

pub fn init() -> Result<()> {
    // Initialize OpenTelemetry tracer if Jaeger endpoint is provided
    let tracer = if let Ok(jaeger_endpoint) = std::env::var("JAEGER_ENDPOINT") {
        opentelemetry_otlp::new_pipeline()
            .tracing()
            .with_exporter(
                opentelemetry_otlp::new_exporter()
                    .tonic()
                    .with_endpoint(jaeger_endpoint)
            )
            .with_trace_config(
                trace::config().with_resource(Resource::new(vec![
                    KeyValue::new("service.name", "event-store"),
                    KeyValue::new("service.version", "1.0.0"),
                ]))
            )
            .install_batch(opentelemetry_sdk::runtime::Tokio)
            .map_err(|e| anyhow::anyhow!("Failed to initialize tracer: {}", e))?
    } else {
        // Fallback to no-op tracer
        opentelemetry::global::set_text_map_propagator(opentelemetry_jaeger::Propagator::new());
        trace::TracerProvider::builder()
            .with_config(
                trace::config().with_resource(Resource::new(vec![
                    KeyValue::new("service.name", "event-store"),
                    KeyValue::new("service.version", "1.0.0"),
                ]))
            )
            .build()
            .tracer("event-store")
    };

    // Initialize tracing subscriber
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::fmt::layer()
                .with_target(false)
                .with_thread_ids(true)
                .with_file(true)
                .with_line_number(true)
                .json()
        )
        .with(EnvFilter::from_default_env().add_directive("event_store=info".parse()?))
        .with(tracing_opentelemetry::layer().with_tracer(tracer))
        .init();

    Ok(())
}
