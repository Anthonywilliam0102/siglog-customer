import asyncio

from sqlalchemy import select

from src.infrastructure import models as m
from src.infrastructure.outbox_publisher import publish_pending


def test_outbox_publica_e_marca_como_publicado(session_factory):
    with session_factory() as s:
        s.add(m.OutboxEvent(routing_key="customer.pedido.criado", payload={"event_id": "1"}))
        s.commit()

    enviados = []

    async def fake_publish(rk, payload):
        enviados.append((rk, payload))

    with session_factory() as s:
        assert asyncio.run(publish_pending(s, fake_publish)) == 1
    with session_factory() as s:
        assert asyncio.run(publish_pending(s, fake_publish)) == 0  # nada pendente
        assert s.scalar(select(m.OutboxEvent)).published_at is not None
    assert enviados == [("customer.pedido.criado", {"event_id": "1"})]
