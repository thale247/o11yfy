import time
import random
import os
import uuid
import logging

from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter

from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter


# -----------------------------
# CONFIG
# -----------------------------
STATION_ID = os.getenv("STATION_ID", str(uuid.uuid4())[:8])
LOCATION = os.getenv("LOCATION", "unknown-location")
OTEL_ENDPOINT = os.getenv("OTEL_ENDPOINT", "http://localhost:4318")


# -----------------------------
# RESOURCE (IMPORTANT FOR GRAFANA GROUPING)
# -----------------------------
resource = Resource.create({
    "service.name": "charger-api-simulator",
    "service.version": "1.0.0",
    "station.id": STATION_ID,
    "station.location": LOCATION,
})


# -----------------------------
# TRACES
# -----------------------------
tracer_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

trace_exporter = OTLPSpanExporter(endpoint=f"{OTEL_ENDPOINT}/v1/traces")
tracer_provider.add_span_processor(
    BatchSpanProcessor(trace_exporter)
)


# -----------------------------
# METRICS
# -----------------------------
metric_exporter = OTLPMetricExporter(endpoint=f"{OTEL_ENDPOINT}/v1/metrics")

metrics.set_meter_provider(
    MeterProvider(
        resource=resource,
        metric_readers=[
            PeriodicExportingMetricReader(
                metric_exporter,
                export_interval_millis=5000
            )
        ]
    )
)

meter = metrics.get_meter(__name__)

# Dashboard-compatible metrics
requests_counter = meter.create_counter(
    name="http_server_requests_seconds_count",
    description="Total simulated requests"
)

errors_counter = meter.create_counter(
    name="http_server_requests_seconds_count",
    description="Error requests"
)

latency_histogram = meter.create_histogram(
    name="http_server_requests_seconds",
    description="Request latency",
    unit="s"
)

available_gauge = meter.create_up_down_counter(
    name="station_available_chargers",
    description="Available chargers"
)


# -----------------------------
# LOGS
# -----------------------------
logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_record_processor(
    BatchLogRecordProcessor(
        OTLPLogExporter(endpoint=f"{OTEL_ENDPOINT}/v1/logs")
    )
)

otel_handler = LoggingHandler(logger_provider=logger_provider)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("charger-station")
logger.addHandler(otel_handler)


# -----------------------------
# STATE
# -----------------------------
available = random.randint(5, 20)


# -----------------------------
# SIMULATION LOOP
# -----------------------------
while True:
    time.sleep(random.uniform(0.5, 2.5))

    start_time = time.time()

    action = random.choices(
        ["rent", "fail", "return", "idle"],
        weights=[0.5, 0.1, 0.3, 0.1]
    )[0]

    status = "200"

    with tracer.start_as_current_span("station_event") as span:
        span.set_attribute("station.id", STATION_ID)
        span.set_attribute("station.location", LOCATION)

        if action == "rent" and available > 0:
            available -= 1
            span.set_attribute("event.type", "rent")
            span.set_attribute("chargers.remaining", available)

            logger.info("charger rented", extra={"station": STATION_ID})

        elif action == "fail":
            status = "500"
            span.set_attribute("event.type", "failure")
            span.set_attribute("reason", "payment_or_unlock_error")

            logger.warning("rental failed", extra={"station": STATION_ID})

        elif action == "return":
            available += 1
            span.set_attribute("event.type", "return")

            logger.info("charger returned", extra={"station": STATION_ID})

        else:
            span.set_attribute("event.type", "idle")

        # -----------------------------
        # DASHBOARD METRICS
        # -----------------------------
        latency = time.time() - start_time

        requests_counter.add(
            1,
            {
                "station.id": STATION_ID,
                "status": status
            }
        )

        if status == "500":
            errors_counter.add(
                1,
                {"station.id": STATION_ID}
            )

        latency_histogram.record(
            latency,
            {
                "station.id": STATION_ID,
                "status": status
            }
        )

        available_gauge.add(0)