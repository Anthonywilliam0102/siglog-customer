import asyncio

from src.api.carga import LimiteDeRequisicoes


def _scope(path="/orders"):
    return {"type": "http", "path": path}


def test_excesso_recebe_503_imediato_e_health_continua():
    liberar = None
    respostas = []

    async def app_lento(scope, receive, send):
        await liberar.wait()
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok"})

    async def chamar(mw, path):
        msgs = []

        async def send(m):
            msgs.append(m)

        await mw(_scope(path), None, send)
        return msgs[0]["status"]

    async def cenario():
        nonlocal liberar
        liberar = asyncio.Event()
        mw = LimiteDeRequisicoes(app_lento, maximo=1)
        primeira = asyncio.create_task(chamar(mw, "/orders"))
        await asyncio.sleep(0)  # a primeira ocupa a única vaga
        respostas.append(await chamar(mw, "/orders"))  # excesso: 503 sem esperar
        respostas.append(("health", mw.em_andamento))
        liberar.set()
        respostas.append(await primeira)
        respostas.append(await chamar(mw, "/orders"))  # vaga liberada

    asyncio.run(cenario())
    assert respostas == [503, ("health", 1), 200, 200]


def test_zero_desliga_o_limite():
    async def app_ok(scope, receive, send):
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    msgs = []

    async def send(m):
        msgs.append(m)

    asyncio.run(LimiteDeRequisicoes(app_ok, maximo=0)(_scope(), None, send))
    assert msgs[0]["status"] == 200
