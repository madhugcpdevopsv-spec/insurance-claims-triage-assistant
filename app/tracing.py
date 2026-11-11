from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor


# STEP 11 uses console export so spans are locally inspectable without adding
# the Collector/Jaeger infrastructure, which is introduced in STEP 12.
_provider = TracerProvider(
    resource=Resource.create({"service.name": "insurance-claims-triage-assistant"})
)
_provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(_provider)

tracer = trace.get_tracer("insurance_claims_triage", "0.1.0")


def current_trace_id() -> str:
    """Return the active trace ID as 32 lowercase hex characters."""
    span_context = trace.get_current_span().get_span_context()
    if not span_context.is_valid:
        return ""
    return f"{span_context.trace_id:032x}"
