"""Camada API do SIG-Log Customer (CRM, SAC & Portal do Cliente).

Fase 0: apenas health check e métricas. Endpoints de negócio (A.6) vêm nas próximas fases.
"""
import json
import logging
import time

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from sqlalchemy.exc import IntegrityError

from src.api.routes import router
from src.config.settings import settings
from src.domain.errors import DomainError
from src.infrastructure.db import SessionLocal, engine
from src.infrastructure.domain_metrics import DomainCollector
from src.infrastructure.telemetry import setup_tracing

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(settings.service_name)

REQUESTS_TOTAL = Counter("requests_total", "Total de requisições", ["method", "path", "status"])
REQUEST_DURATION = Histogram("request_duration", "Duração das requisições (s)", ["method", "path"])
ERRORS_TOTAL = Counter("errors_total", "Total de respostas 5xx", ["path"])
ACTIVE_REQUESTS = Gauge("active_requests", "Requisições em andamento")

app = FastAPI(
    title="SIG-Log Customer",
    description="CRM, SAC & Portal do Cliente — Squad 06",
    version="0.1.0",
)


if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware, allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
        allow_methods=["GET", "POST", "PATCH"], allow_headers=["Authorization", "Content-Type"])
app.include_router(router)
setup_tracing(app, engine)
REGISTRY.register(DomainCollector(SessionLocal))


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    log_event("domain_error", level="WARNING", path=request.url.path, detail=exc.message)
    return JSONResponse(status_code=exc.status, content={"detail": exc.message})


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    log_event("integrity_error", level="WARNING", path=request.url.path)
    return JSONResponse(status_code=409, content={"detail": "Conflito: o registro já existe ou foi alterado"})


def log_event(event: str, level: str = "INFO", **extra) -> None:
    log.info(json.dumps({
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "service": settings.service_name,
        "event": event,
        "level": level,
        **extra,
    }))


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    ACTIVE_REQUESTS.inc()
    start = time.perf_counter()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        ACTIVE_REQUESTS.dec()
        # Template da rota (/orders/{order_id}), nunca o path real: evita uma série por UUID.
        route = request.scope.get("route")
        path = getattr(route, "path", None) or "unmatched"
        REQUEST_DURATION.labels(request.method, path).observe(time.perf_counter() - start)
        REQUESTS_TOTAL.labels(request.method, path, str(status)).inc()
        if status >= 500:
            ERRORS_TOTAL.labels(path).inc()


@app.get("/health", tags=["infra"])
def health() -> dict:
    return {"status": "ok", "service": settings.service_name}


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
