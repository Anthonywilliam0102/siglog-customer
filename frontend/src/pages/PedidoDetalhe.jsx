import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api } from '../api.js';
import Confirmar from '../components/Confirmar.jsx';
import { useToast } from '../components/Toast.jsx';
import Voltar from '../components/Voltar.jsx';
import { Alerta, Cabecalho, Carregando, Estrelas, SeloPedido } from '../components/ui.jsx';
import { useAuth } from '../auth.jsx';
import { useCarga } from '../hooks.js';
import { brl, curto, dataHora, ETAPAS, PROXIMOS, STATUS_PEDIDO } from '../lib.js';

function Linha({ status }) {
  if (status === 'CANCELADO') return <p><SeloPedido status="CANCELADO" /></p>;
  const atual = ETAPAS.indexOf(status);
  return (
    <ol className="linha" aria-label="Andamento do pedido">
      {ETAPAS.map((e, i) => (
        <li key={e} className={i < atual ? 'feito' : i === atual ? 'atual' : ''} aria-current={i === atual ? 'step' : undefined}>
          {STATUS_PEDIDO[e].label}
        </li>
      ))}
    </ol>
  );
}

function Rastreamento({ id }) {
  const { dados, erro, carregando } = useCarga(() => api(`/orders/${id}/tracking`), [id]);
  return (
    <section className="cartao">
      <h2>Rastreamento</h2>
      {carregando ? <Carregando /> : erro ? <Alerta tipo="info">Rastreamento indisponível no momento. {erro}</Alerta> : (
        <>
          <p><b>{dados.status}</b>{dados.source === 'mock' && <span className="muted"> · simulado (demonstração)</span>}</p>
          {dados.events.length === 0 ? <p className="muted">Ainda sem movimentações.</p> : (
            <ul className="eventos">
              {dados.events.map((ev, i) => (
                <li key={i}><time>{dataHora(ev.timestamp)}</time> {ev.description}</li>
              ))}
            </ul>
          )}
        </>
      )}
    </section>
  );
}

function Avaliar({ pedido }) {
  const toast = useToast();
  const [nota, setNota] = useState(0);
  const [feito, setFeito] = useState(false);
  const [erro, setErro] = useState('');
  async function enviar(e) {
    e.preventDefault();
    if (!nota) return setErro('Escolha uma nota de 1 a 5.');
    try {
      await api('/feedback', { method: 'POST', body: { target: 'ENTREGA', nota, order_id: pedido.id, comentario: new FormData(e.target).get('comentario') || null } });
      setFeito(true);
      toast.ok('Avaliação registrada. Obrigado!');
    } catch (err) {
      if (err.status === 409) setFeito(true);
      else setErro(err.message);
    }
  }
  return (
    <section className="cartao">
      <h2>Avaliar a entrega</h2>
      {feito ? <Alerta tipo="ok">Obrigado! Sua avaliação foi registrada.</Alerta> : (
        <form onSubmit={enviar}>
          <Estrelas valor={nota} onChange={setNota} />
          <label className="campo"><span>Comentário (opcional)</span><textarea name="comentario" rows={3} /></label>
          <Alerta>{erro}</Alerta>
          <button className="primario">Enviar avaliação</button>
        </form>
      )}
    </section>
  );
}

export default function PedidoDetalhe() {
  const { id } = useParams();
  const { equipe } = useAuth();
  const { dados: p, erro, carregando, recarregar } = useCarga(() => api(`/orders/${id}`), [id]);
  const [msg, setMsg] = useState('');
  const [cancelando, setCancelando] = useState(false);
  const toast = useToast();

  async function mudar(status) {
    setMsg('');
    try {
      await api(`/orders/${id}/status`, { method: 'PATCH', body: { status } });
      toast.ok(status === 'CANCELADO' ? 'Pedido cancelado.' : `Status atualizado: ${STATUS_PEDIDO[status].label}.`);
      recarregar();
    } catch (err) {
      setMsg(err.message);
      toast.erro(err.message);
    }
  }

  if (carregando) return <div className="pagina"><Carregando /></div>;
  if (erro) return <div className="pagina"><Alerta>{erro}</Alerta><Link to="/pedidos">Voltar</Link></div>;

  return (
    <div className="pagina">
      <Voltar para="/pedidos" />
      <Cabecalho titulo={`Pedido #${curto(p.id)}`} subtitulo={`${p.origem} → ${p.destino} · ${brl(p.valor_estimado)} · criado em ${dataHora(p.created_at)}`}
        acao={<SeloPedido status={p.status} />} />
      <section className="cartao"><Linha status={p.status} /></section>
      <Rastreamento id={p.id} key={p.status} />
      <section className="acoes">
        <Link className="botao" to={`/chamados/novo?pedido=${p.id}`}>Abrir chamado</Link>
        {p.status !== 'CANCELADO' && <Link className="botao" to={`/sinistros/novo?pedido=${p.id}`}>Registrar sinistro</Link>}
      </section>
      {equipe && PROXIMOS[p.status].length > 0 && (
        <section className="cartao">
          <h2>Atualizar status (equipe)</h2>
          <div className="acoes">
            {PROXIMOS[p.status].map((s) => (
              <button key={s} className={s === 'CANCELADO' ? 'perigo' : 'primario'} onClick={() => (s === 'CANCELADO' ? setCancelando(true) : mudar(s))}>
                {s === 'CANCELADO' ? 'Cancelar pedido' : `Marcar como ${STATUS_PEDIDO[s].label.toLowerCase()}`}
              </button>
            ))}
          </div>
          <Alerta>{msg}</Alerta>
        </section>
      )}
      {!equipe && p.status === 'ENTREGUE' && <Avaliar pedido={p} />}
      <Confirmar aberto={cancelando} titulo="Cancelar este pedido?" texto="O cancelamento não pode ser desfeito e o pedido deixa de aceitar novas movimentações." rotulo="Cancelar pedido" perigo
        onCancelar={() => setCancelando(false)} onConfirmar={() => { setCancelando(false); mudar('CANCELADO'); }} />
    </div>
  );
}
