"""Worker do Outbox: publica no RabbitMQ os eventos gravados pelo serviço.

Execução: python -m src.infrastructure.outbox_publisher
Entrega at-least-once: se o processo cair após publicar e antes do commit, o evento é reenviado;
consumidores devem deduplicar por `event_id`.
"""
import asyncio
import json
import logging
from collections.abc import Awaitable, Callable

import aio_pika
from prometheus_client import Counter, start_http_server
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.config.settings import settings
from src.domain.rules import utcnow
from src.infrastructure.db import SessionLocal
from src.infrastructure.models import OutboxEvent

log = logging.getLogger("outbox")
MESSAGES_PUBLISHED = Counter("messages_processed_total", "Mensagens publicadas no broker", ["routing_key"])
Publish = Callable[[str, dict], Awaitable[None]]


def _fetch(session: Session, batch: int) -> list[OutboxEvent]:
    return list(session.scalars(
        select(OutboxEvent).where(OutboxEvent.published_at.is_(None))
        .order_by(OutboxEvent.created_at).limit(batch).with_for_update(skip_locked=True)))


def _mark_published(session: Session, rows: list[OutboxEvent]) -> None:
    for row in rows:
        row.published_at = utcnow()
    session.commit()


async def publish_pending(session: Session, publish: Publish, batch: int = 50) -> int:
    """Publica o lote. Acesso ao banco roda em thread (não bloqueia o event loop do aio-pika).

    Se um publish falhar no meio, o que já foi publicado é marcado antes de propagar o erro
    (menos reenvios); o restante continua pendente para a próxima tentativa.
    """
    rows = await asyncio.to_thread(_fetch, session, batch)
    done: list[OutboxEvent] = []
    try:
        for row in rows:
            await publish(row.routing_key, row.payload)
            MESSAGES_PUBLISHED.labels(row.routing_key).inc()
            done.append(row)
    finally:
        await asyncio.to_thread(_mark_published, session, done)
    return len(done)


async def connect_with_retry(delay: float = 3.0):
    """O healthcheck do RabbitMQ pode ficar verde antes da porta AMQP aceitar conexões."""
    while True:
        try:
            return await aio_pika.connect_robust(settings.rabbitmq_url)
        except Exception as exc:  # noqa: BLE001
            log.warning(json.dumps({"service": settings.service_name, "event": "rabbitmq_unavailable",
                                    "level": "WARNING", "detail": repr(exc)[:200]}))
            await asyncio.sleep(delay)


async def main() -> None:
    start_http_server(settings.worker_metrics_port)
    connection = await connect_with_retry()
    async with connection:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(settings.events_exchange, aio_pika.ExchangeType.TOPIC, durable=True)

        async def publish(routing_key: str, payload: dict) -> None:
            await exchange.publish(
                aio_pika.Message(json.dumps(payload).encode(), content_type="application/json",
                                 delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                                 message_id=payload.get("event_id")),
                routing_key=routing_key)

        while True:
            try:
                with SessionLocal() as session:
                    sent = await publish_pending(session, publish)
            except Exception as exc:  # noqa: BLE001 - o worker não pode morrer por uma falha pontual
                log.error(json.dumps({"service": settings.service_name, "event": "outbox_error",
                                      "level": "ERROR", "detail": repr(exc)}))
                await asyncio.sleep(5)
                continue
            if sent:
                log.info(json.dumps({"service": settings.service_name, "event": "outbox_published", "count": sent}))
            else:
                await asyncio.sleep(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    asyncio.run(main())
