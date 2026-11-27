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


def test_falha_no_meio_do_lote_marca_o_que_ja_foi_publicado(session_factory):
    with session_factory() as s:
        for i in range(3):
            s.add(m.OutboxEvent(routing_key=f"k{i}", payload={"event_id": str(i)}))
        s.commit()

    async def publish_com_erro(rk, payload):
        if rk == "k2":
            raise RuntimeError("broker recusou")

    with session_factory() as s:
        try:
            asyncio.run(publish_pending(s, publish_com_erro))
        except RuntimeError:
            pass
    with session_factory() as s:
        pendentes = [e.routing_key for e in s.scalars(select(m.OutboxEvent)) if e.published_at is None]
    assert pendentes == ["k2"]
