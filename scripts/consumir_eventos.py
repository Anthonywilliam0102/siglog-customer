"""Consumidor de EXEMPLO dos eventos do CRM no RabbitMQ (também serve para provar a entrega).

Cria uma fila durável própria ligada ao exchange `siglog.events`, imprime cada evento e confirma (ack).
Os outros squads podem copiar este arquivo como ponto de partida. Deduplica por `event_id` (entrega at-least-once).

Uso:
  RABBITMQ_URL=amqp://usuario:senha@host:5672/ \\
    python scripts/consumir_eventos.py --fila wms-pedidos --chave customer.pedido.criado --max 5
  # várias chaves:  --chave customer.pedido.criado --chave customer.sinistro.registrado     (padrão: customer.#)
"""
import argparse
import asyncio
import json
import os

import aio_pika

EXCHANGE = os.environ.get("EVENTS_EXCHANGE", "siglog.events")


async def principal(args) -> int:
    conexao = await aio_pika.connect_robust(os.environ["RABBITMQ_URL"])
    vistos: set[str] = set()
    recebidos = 0
    async with conexao:
        canal = await conexao.channel()
        exchange = await canal.declare_exchange(EXCHANGE, aio_pika.ExchangeType.TOPIC, durable=True)
        fila = await canal.declare_queue(args.fila, durable=True)
        for chave in args.chave or ["customer.#"]:
            await fila.bind(exchange, routing_key=chave)
        print(f"Aguardando eventos em '{args.fila}' (exchange {EXCHANGE})…")
        try:
            async with asyncio.timeout(args.timeout):
                async with fila.iterator() as it:
                    async for msg in it:
                        async with msg.process():  # ack ao sair do bloco sem erro
                            ev = json.loads(msg.body)
                            if ev["event_id"] in vistos:
                                print("duplicado, ignorando", ev["event_id"])
                                continue
                            vistos.add(ev["event_id"])
                            recebidos += 1
                            print(f"{ev['occurred_at']}  {ev['event_type']:<20} {msg.routing_key:<30} id={ev['event_id'][:8]}")
                            if recebidos >= args.max:
                                break
        except TimeoutError:
            print("tempo esgotado sem novos eventos")
    print(f"Total recebido: {recebidos}")
    return 0 if recebidos else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fila", required=True)
    ap.add_argument("--chave", action="append")
    ap.add_argument("--max", type=int, default=10)
    ap.add_argument("--timeout", type=float, default=60)
    raise SystemExit(asyncio.run(principal(ap.parse_args())))
