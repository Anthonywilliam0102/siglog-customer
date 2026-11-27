import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { api } from '../api.js';
import { useToast } from '../components/Toast.jsx';
import Voltar from '../components/Voltar.jsx';
import { Cabecalho } from '../components/ui.jsx';
import SeletorCliente, { useClienteId } from '../components/SeletorCliente.jsx';
import { useCarga } from '../hooks.js';
import { curto, dataHora, STATUS_PEDIDO } from '../lib.js';

const TEMAS = [['ATRASO', 'Atraso na entrega'], ['ENTREGA', 'Onde está minha entrega?'], ['COBRANCA', 'Cobrança e pagamento'],
  ['DUVIDA', 'Tenho uma dúvida'], ['OUTRO', 'Outro assunto']];
const pausa = (ms) => new Promise((r) => { setTimeout(r, ms); });

// Respostas prontas (regras fixas, sem IA) montadas com os dados reais do pedido, inclusive o que WMS/Financeiro/Tracking informam.
async function responder(tema, pedidoId) {
  const [o, trk, sq] = await Promise.all([
    api(`/orders/${pedidoId}`),
    api(`/orders/${pedidoId}/tracking`).catch(() => null),
    api(`/orders/${pedidoId}/squads`).catch(() => []),
  ]);
  const wms = sq.find((x) => x.squad === 'wms');
  const fin = sq.find((x) => x.squad === 'financeiro');
  const base = `Seu pedido #${curto(o.id)} (${o.origem} → ${o.destino}) está em “${STATUS_PEDIDO[o.status].label}”.`;
  const ultimo = trk?.events?.length ? trk.events[trk.events.length - 1] : null;
  const rastro = ultimo ? `Última movimentação: ${ultimo.description} (${dataHora(ultimo.timestamp)}).` : null;
  const sep = wms?.status ? `Separação no centro de distribuição: ${wms.status}${wms.detalhes?.[0] ? ` (${wms.detalhes[0].valor})` : ''}.` : null;
  if (tema === 'COBRANCA') {
    return [base, fin?.status ? `Cobrança: ${fin.status}${fin.detalhes?.length ? ` · ${fin.detalhes.map((d) => `${d.rotulo.toLowerCase()} ${d.valor}`).join(' · ')}` : ''}.` : 'Ainda não consegui consultar a cobrança deste pedido.'];
  }
  if (o.status === 'ENTREGUE') return [base, 'Ele consta como entregue. Se você não recebeu ou houve algum problema com a carga, vale falar com a nossa equipe.'];
  if (o.status === 'CANCELADO') return [base, 'Pedidos cancelados não seguem para transporte.'];
  if (o.status === 'EM_TRANSPORTE') return [base, 'A carga já saiu e está a caminho.', rastro].filter(Boolean);
  return [base, 'A carga ainda não saiu do centro de distribuição.', sep].filter(Boolean);
}

export default function NovoChamado() {
  const nav = useNavigate();
  const toast = useToast();
  const [params] = useSearchParams();
  const [escolhido, setEscolhido] = useState('');
  const clienteId = useClienteId(escolhido);
  const pedidos = useCarga(() => (clienteId ? api(`/orders?limit=5&customer_id=${clienteId}`) : []), [clienteId]);
  const [msgs, setMsgs] = useState([{ de: 'bot', texto: 'Olá! Sou o assistente automático do atendimento. Sobre o que você quer falar?' }]);
  const [etapa, setEtapa] = useState('tema');
  const [tema, setTema] = useState(null);
  const [pedido, setPedido] = useState(params.get('pedido') || null);
  const [ocupado, setOcupado] = useState(false);
  const fim = useRef(null);

  useEffect(() => { fim.current?.scrollIntoView?.({ block: 'end', behavior: 'smooth' }); }, [msgs, etapa, ocupado]);

  const eu = (texto) => setMsgs((m) => [...m, { de: 'eu', texto }]);
  async function bot(...textos) {
    for (const t of textos.flat()) {
      setOcupado(true);
      await pausa(450);
      setMsgs((m) => [...m, { de: 'bot', texto: t }]);
    }
    setOcupado(false);
  }

  async function aoEscolherTema([id, rotulo]) {
    eu(rotulo);
    setTema([id, rotulo]);
    if (pedido) return consultar(id, pedido);
    if (['ATRASO', 'ENTREGA', 'COBRANCA'].includes(id) && (pedidos.dados ?? []).length) {
      await bot('Sobre qual pedido?');
      return setEtapa('pedido');
    }
    await bot('Pode me contar o que aconteceu? Escreva abaixo e já abro um chamado para a nossa equipe.');
    return setEtapa('descrever');
  }

  async function consultar(id, pid) {
    setEtapa('aguarde');
    try {
      await bot(await responder(id, pid), 'Isso resolveu a sua dúvida?');
      setEtapa('resolveu');
    } catch {
      await bot('Não consegui consultar o pedido agora. Descreva o que aconteceu e a nossa equipe verifica para você.');
      setEtapa('descrever');
    }
  }

  async function aoEscolherPedido(p) {
    if (!p) { eu('Nenhum pedido'); await bot('Tudo bem. Pode me contar o que aconteceu?'); return setEtapa('descrever'); }
    eu(`#${curto(p.id)} · ${p.origem} → ${p.destino}`);
    setPedido(p.id);
    return consultar(tema[0], p.id);
  }

  async function aoResolver(sim) {
    eu(sim ? 'Sim, resolveu' : 'Não, quero falar com a equipe');
    if (sim) { await bot('Que bom! Se precisar de mais alguma coisa, é só chamar.'); return setEtapa('fim'); }
    await bot('Sem problema. Descreva o que está acontecendo e já abro um chamado para a nossa equipe.');
    return setEtapa('descrever');
  }

  async function enviar(e) {
    e.preventDefault();
    const texto = new FormData(e.target).get('mensagem').trim();
    if (texto.length < 2 || !clienteId) return;
    eu(texto);
    setEtapa('aguarde');
    try {
      const [id, rotulo] = tema ?? ['OUTRO', 'Outro assunto'];
      const t = await api('/tickets', {
        method: 'POST',
        body: { customer_id: clienteId, order_id: pedido || null, categoria: id, prioridade: id === 'ATRASO' ? 'ALTA' : 'MEDIA',
          assunto: `${rotulo}${pedido ? ` · pedido #${curto(pedido)}` : ''}`, mensagem: texto },
      });
      toast.ok('Chamado aberto. A conversa continua aqui.');
      nav(`/chamados/${t.id}`);
    } catch (err) {
      await bot(`Não consegui abrir o chamado: ${err.message}`);
      setEtapa('descrever');
    }
  }

  const aguardandoCliente = !clienteId;
  return (
    <div className="pagina estreita">
      <Voltar para="/chamados" />
      <Cabecalho titulo="Atendimento" subtitulo="Converse com o assistente. Se ele não resolver, a nossa equipe assume." />
      <SeletorCliente valor={escolhido} onChange={setEscolhido} />
      <section className="chat" aria-label="Conversa com o assistente" aria-live="polite">
        <div className="chat-msgs">
          {msgs.map((m, i) => (
            <div key={i} className={`bolha ${m.de}`}>
              {m.de === 'bot' && <span className="bolha-autor">Assistente automático</span>}
              <p>{m.texto}</p>
            </div>
          ))}
          {ocupado && <div className="bolha bot digitando" aria-label="Assistente digitando"><span /><span /><span /></div>}
          <div ref={fim} />
        </div>
        <div className="chat-acao">
          {etapa === 'tema' && !aguardandoCliente && (
            <div className="chips">{TEMAS.map((t) => <button key={t[0]} type="button" onClick={() => aoEscolherTema(t)}>{t[1]}</button>)}</div>
          )}
          {etapa === 'tema' && aguardandoCliente && <p className="muted">Escolha o cliente atendido para começar.</p>}
          {etapa === 'pedido' && !ocupado && (
            <div className="chips">
              {(pedidos.dados ?? []).map((p) => <button key={p.id} type="button" onClick={() => aoEscolherPedido(p)}>#{curto(p.id)} · {p.origem} → {p.destino}</button>)}
              <button type="button" onClick={() => aoEscolherPedido(null)}>Nenhum pedido</button>
            </div>
          )}
          {etapa === 'resolveu' && !ocupado && (
            <div className="chips"><button type="button" onClick={() => aoResolver(true)}>Sim, resolveu</button><button type="button" onClick={() => aoResolver(false)}>Não, quero falar com a equipe</button></div>
          )}
          {etapa === 'fim' && !ocupado && <div className="chips"><Link className="botao" to="/">Voltar ao início</Link><Link className="botao" to="/chamados">Meus chamados</Link></div>}
          {etapa === 'descrever' && !ocupado && (
            <form className="compositor" onSubmit={enviar}>
              <textarea name="mensagem" rows={2} required placeholder="Escreva aqui o que aconteceu… (Enter envia)" aria-label="Sua mensagem"
                onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); e.target.form.requestSubmit(); } }} />
              <button className="primario" disabled={aguardandoCliente}>Enviar</button>
            </form>
          )}
        </div>
      </section>
    </div>
  );
}
