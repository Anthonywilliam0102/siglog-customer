"""OpenTelemetry (traces -> Jaeger via OTLP/HTTP). Desligado quando OTEL_EXPORTER_OTLP_ENDPOINT é vazio."""
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from src.config.settings import settings


def setup_tracing(app, engine) -> bool:
    if not settings.otel_exporter_otlp_endpoint:
        return False
    provider = TracerProvider(resource=Resource.create({"service.name": settings.service_name}))
    exporter = OTLPSpanExporter(endpoint=f"{settings.otel_exporter_otlp_endpoint.rstrip('/')}/v1/traces")
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app, excluded_urls="metrics,health")
    SQLAlchemyInstrumentor().instrument(engine=engine)
    return True
