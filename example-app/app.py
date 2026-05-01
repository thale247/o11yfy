import random
import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response, status

# --- OpenTelemetry ---
from opentelemetry import trace, metrics
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

# ---- Logging ----
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---- Resource ----
resource = Resource.create({
    "service.name": "o11yfy-demo-api",
    "service.version": "1.0.0",
    "environment": "local",
})

# ---- Metrics: Response Time ----
http_response_time = None

def setup_metrics_meter():
    global http_response_time

    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(
            endpoint="http://localhost:4317",
            insecure=True,
            timeout=5,
        ),
        export_interval_millis=5000,
    )

    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[metric_reader],
    )
    metrics.set_meter_provider(meter_provider)

    meter = metrics.get_meter(__name__)

    http_response_time = meter.create_histogram(
        name="http.server.duration",
        description="HTTP request duration",
        unit="ms",
    )

    return meter_provider


# ---- Helper for consistent metric recording ----
def record_response_time(endpoint: str, duration_ms: float, status_code: int = 200):
    if http_response_time:
        http_response_time.record(
            duration_ms,
            {
                "endpoint": endpoint,
                "status_code": str(status_code),
            },
        )


# ---- Tracing ----
def setup_tracing():
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    try:
        exporter = OTLPSpanExporter(
            endpoint="http://localhost:4317",
            insecure=True,
            timeout=5,
        )
        provider.add_span_processor(BatchSpanProcessor(exporter))
        logger.info("✓ OTLP tracing enabled")
    except Exception as e:
        logger.warning(f"Tracing exporter failed: {e}")

    return provider


tracer_provider = setup_tracing()
meter_provider = setup_metrics_meter()

tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# ---- Custom Metrics ----
request_counter = meter.create_counter(
    "http.requests.total",
    description="Total HTTP requests",
)

error_counter = meter.create_counter(
    "http.errors.total",
    description="Total HTTP errors",
)

spike_counter = meter.create_counter(
    "application.spikes.total",
    description="Spike events",
)

active_requests = meter.create_up_down_counter(
    "http.requests.active",
    description="Active requests",
)

# ---- App lifecycle ----
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup")
    yield
    logger.info("shutdown")


app = FastAPI(title="o11yfy-demo-api", lifespan=lifespan)

# ---- Auto instrumentation ----
FastAPIInstrumentor.instrument_app(app)
RequestsInstrumentor().instrument()
URLLib3Instrumentor().instrument()


# ---- Endpoints ----

@app.get("/")
def root():
    start = time.time()

    with tracer.start_as_current_span("root"):
        request_counter.add(1, {"endpoint": "root"})
        active_requests.add(1)
        try:
            return {"status": "ok"}
        finally:
            duration = (time.time() - start) * 1000
            record_response_time("root", duration, 200)
            active_requests.add(-1)


@app.get("/fast")
def fast():
    start = time.time()

    with tracer.start_as_current_span("fast"):
        request_counter.add(1, {"endpoint": "fast"})
        active_requests.add(1)
        try:
            return {"message": "fast"}
        finally:
            duration = (time.time() - start) * 1000
            record_response_time("fast", duration, 200)
            active_requests.add(-1)


@app.get("/slow")
def slow():
    start = time.time()

    with tracer.start_as_current_span("slow") as span:
        request_counter.add(1, {"endpoint": "slow"})
        active_requests.add(1)
        try:
            delay = random.uniform(0.5, 2.5)
            span.set_attribute("delay", delay)
            time.sleep(delay)
            return {"delay": delay}
        finally:
            duration = (time.time() - start) * 1000
            record_response_time("slow", duration, 200)
            active_requests.add(-1)


@app.get("/spiky")
def spiky():
    start = time.time()

    with tracer.start_as_current_span("spiky") as span:
        request_counter.add(1, {"endpoint": "spiky"})
        active_requests.add(1)
        try:
            if random.random() < 0.2:
                spike_counter.add(1)
                delay = random.uniform(3, 6)
                span.set_attribute("spike", True)
                time.sleep(delay)
                return {"spike": True, "delay": delay}

            span.set_attribute("spike", False)
            return {"spike": False}
        finally:
            duration = (time.time() - start) * 1000
            record_response_time("spiky", duration, 200)
            active_requests.add(-1)


@app.get("/error")
def error(response: Response):
    start = time.time()

    with tracer.start_as_current_span("error"):
        active_requests.add(1)
        try:
            if random.random() < 0.3:
                error_counter.add(1, {"endpoint": "error"})
                request_counter.add(1, {"endpoint": "error", "status": "500"})
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                return {"error": "failed"}

            request_counter.add(1, {"endpoint": "error", "status": "200"})
            return {"ok": True}

        finally:
            duration = (time.time() - start) * 1000
            record_response_time("error", duration, response.status_code)
            active_requests.add(-1)


@app.get("/mixed")
def mixed(response: Response):
    start = time.time()

    with tracer.start_as_current_span("mixed") as span:
        request_counter.add(1, {"endpoint": "mixed"})
        active_requests.add(1)
        try:
            r = random.random()

            if r < 0.2:
                delay = random.uniform(2, 5)
                span.set_attribute("type", "slow")
                time.sleep(delay)
                return {"type": "slow"}

            if r < 0.4:
                error_counter.add(1)
                span.set_attribute("type", "error")
                response.status_code = 500
                return {"type": "error"}

            span.set_attribute("type", "normal")
            return {"type": "normal"}

        finally:
            duration = (time.time() - start) * 1000
            record_response_time("mixed", duration, response.status_code)
            active_requests.add(-1)


@app.get("/health")
def health():
    return {"status": "healthy"}