import random
import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response, status
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# ---- Logging ----
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ---- App lifecycle ----
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup")
    yield
    logger.info("shutdown")


app = FastAPI(title="o11yfy-demo-api", lifespan=lifespan)


# ---- Endpoints ----

@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/fast")
def fast():
    return {"message": "fast"}


@app.get("/slow")
def slow():
    delay = random.uniform(0.5, 2.5)
    time.sleep(delay)
    return {"delay": delay}


@app.get("/spiky")
def spiky():
    if random.random() < 0.2:
        delay = random.uniform(3, 6)
        time.sleep(delay)
        return {"spike": True, "delay": delay}

    return {"spike": False}


@app.get("/error")
def error(response: Response):
    if random.random() < 0.3:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": "failed"}

    return {"ok": True}


@app.get("/mixed")
def mixed(response: Response):
    r = random.random()

    if r < 0.2:
        delay = random.uniform(2, 5)
        time.sleep(delay)
        return {"type": "slow"}

    if r < 0.4:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"type": "error"}

    return {"type": "normal"}


@app.get("/health")
def health():
    return {"status": "healthy"}

FastAPIInstrumentor.instrument_app(app)