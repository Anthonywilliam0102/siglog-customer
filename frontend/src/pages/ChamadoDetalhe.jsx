import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api } from '../api.js';
import { Alerta, Cabecalho, Carregando, Estrelas, Selo, SeloTicket } from '../components/ui.jsx';
import { useAuth } from '../auth.jsx';
import { useCarga } from '../hooks.js';
import { curto, dataHora, sla } from '../lib.js';

function AvaliarAtendimento({ ticketId }) {
  const [nota, setNota] = useState(0);
  const [feito, setFeito] = useState(false);
  const [erro, setErro] = useState('');
  async function enviar(e) {
    e.preventDefault();
    if (!nota) return setErro('Escolha uma nota de 1 a 5.');
    try {
      await api('/feedback', { method: 'POST', body: { target: 'ATENDIMENTO', nota, ticket_id: ticketId, comentario: new FormData(e.target).get('comentario') || null } });
      setFeito(true);
    } catch (err) {
      if (err.status === 409) setFeito(true);
      else setErro(err.message);
    }
  }
  return (
    <section className="cartao">
      <h2>Avaliar o atendimento</h2>
      {feito ? <Alerta tipo="ok">Obrigado pela avaliação!</Alerta> : (
        <form onSubmit={enviar}>
          <Estrelas valor={nota} onChange={setNota} />
          <label className="campo"><span>Comentário (opcional)</span><textarea name="comentario" rows={2} /></label>
          <Alerta>{erro}</Alerta>
          <button className="primario">Enviar avaliação</button>
        </form>
      )}
    </section>
  );
}

export default function ChamadoDetalhe() {
  const { id } = useParams();
  const { equipe } = useAuth();
  const { dados: t, erro, carregando, recarregar } = useCarga(() => api(`/tickets/${id}`), [id]);
  const [msgErro, setMsgErro] = useState('');
  const [enviando, setEnviando] = useState(false);

  async function responder(e) {
    e.preventDefault();
    const form = e.target;
    setMsgErro('');
    setEnviando(true);
    try {
      await api(`/tickets/${id}/messages`, { method: 'POST', body: { mensagem: new FormData(form).get('mensagem') } });
      form.reset();
      await recarregar();
    } catch (err) {
      setMsgErro(err.message);
    } finally {
      setEnviando(false);
    }
  }

  async function status(novo) {
    setMsgErro('');
    try {
      await api(`/tickets/${id}/status`, { method: 'PATCH', body: { status: novo } });
      recarregar();
    } catch (err) {
      setMsgErro(err.message);
    }
  }

  if (carregando && !t) return <div className="pagina"><Carregando /></div>;
  if (erro) return <div className="pagina"><Alerta>{erro}</Alerta><Link to="/chamados">Voltar</Link></div>;
  const s = sla(t);

  return (
    <div className="pagina estreita">
      <Cabecalho titulo={t.assunto} subtitulo={`Chamado #${curto(t.id)} · ${t.categoria} · prioridade ${t.prioridade.toLowerCase()}`}
        acao={<div className="acoes"><SeloTicket status={t.status} /><Selo tom={s.tom}>{s.texto}</Selo></div>} />
      {t.order_id && <p><Link to={`/pedidos/${t.order_id}`}>Ver pedido #{curto(t.order_id)}</Link></p>}

      <section className="conversa" aria-label="Mensagens">
        {t.messages.map((m, i) => (
          <article key={i} className={`mensagem ${m.author_role === 'cliente' ? 'cliente' : 'equipe'}`}>
            <header><b>{m.author_role === 'cliente' ? 'Cliente' : 'Atendimento'}</b> · <time>{dataHora(m.created_at)}</time></header>
            <p>{m.mensagem}</p>
          </article>
        ))}
      </section>

      {t.status !== 'RESOLVIDO' ? (
        <form className="cartao" onSubmit={responder}>
          <label className="campo"><span>Responder</span><textarea name="mensagem" rows={3} required /></label>
          <div className="acoes">
            <button className="primario" disabled={enviando}>{enviando ? 'Enviando…' : 'Enviar resposta'}</button>
            {equipe && <button type="button" onClick={() => status('RESOLVIDO')}>Marcar como resolvido</button>}
          </div>
        </form>
      ) : (
        <>
          <Alerta tipo="ok">Este chamado foi resolvido.</Alerta>
          {!equipe && <AvaliarAtendimento ticketId={t.id} />}
        </>
      )}
      <Alerta>{msgErro}</Alerta>
    </div>
  );
}
