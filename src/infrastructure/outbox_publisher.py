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
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.config.settings import settings
from src.domain.rules import utcnow
from src.infrastructure.db import SessionLocal
from src.infrastructure.models import OutboxEvent

log = logging.getLogger("outbox")
Publish = Callable[[str, dict], Awaitable[None]]


async def publish_pending(session: Session, publish: Publish, batch: int = 50) -> int:
    rows = list(session.scalars(
        select(OutboxEvent).where(OutboxEvent.published_at.is_(None))
        .order_by(OutboxEvent.created_at).limit(batch).with_for_update(skip_locked=True)))
    for row in rows:
        await publish(row.routing_key, row.payload)
        row.published_at = utcnow()
    session.commit()
    return len(rows)


async def main() -> None:
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
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
            with SessionLocal() as session:
                sent = await publish_pending(session, publish)
            if sent:
                log.info(json.dumps({"service": settings.service_name, "event": "outbox_published", "count": sent}))
            else:
                await asyncio.sleep(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    asyncio.run(main())
