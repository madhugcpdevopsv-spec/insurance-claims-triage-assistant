from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter


_resource = Resource.create({"service.name": "insurance-claims-triage-assistant"})
_provider = TracerProvider(resource=_resource)

# STEP 12 sends spans to the local OpenTelemetry Collector over OTLP/HTTP.
# Set OTEL_TRACES_EXPORTER=console to use the STEP 11 local console exporter.
if __import__("os").getenv("OTEL_TRACES_EXPORTER", "otlp").lower() == "console":
    _span_exporter = ConsoleSpanExporter()
else:
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

    _span_exporter = OTLPSpanExporter(
        endpoint=__import__("os").getenv(
            "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT",
            "http://localhost:4318/v1/traces",
        )
    )

_provider.add_span_processor(BatchSpanProcessor(_span_exporter))
trace.set_tracer_provider(_provider)

tracer = trace.get_tracer("insurance_claims_triage", "0.1.0")


def current_trace_id() -> str:
    """Return the active trace ID as 32 lowercase hex characters."""
    span_context = trace.get_current_span().get_span_context()
    if not span_context.is_valid:
        return ""
    return f"{span_context.trace_id:032x}"
