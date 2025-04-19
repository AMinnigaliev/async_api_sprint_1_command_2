from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import \
    OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from .config import settings

trace.set_tracer_provider(
    TracerProvider(
        resource=Resource(
            attributes={
                SERVICE_NAME: settings.service_name,
            },
        ),
    ),
)
otlp_exporter = OTLPSpanExporter(endpoint=settings.jaeger_http_endpoint)
span_processor = BatchSpanProcessor(span_exporter=otlp_exporter)

tracer_provider = trace.get_tracer_provider()
tracer_provider.add_span_processor(span_processor)

tracer = trace.get_tracer(__name__)
