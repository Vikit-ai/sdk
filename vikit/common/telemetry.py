import vikit.common.config as config
import vikit.common.secrets as secrets

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure the tracer provider
resource = Resource(attributes={"vikit-ai.sdk": "Vikit.ai SDK"})
trace.set_tracer_provider(TracerProvider(resource=resource))

# Configure the OTLP exporter
otlp_exporter = OTLPSpanExporter(
    endpoint=config.get_telemetry_endpoint(),
    headers=(("Authorization", f"Bearer {secrets.get_telemetry_api_key()}]"),),
)

# Add the exporter to the tracer provider
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Get a tracer
tracer = trace.get_tracer(__name__)
