import { useEffect, useRef, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api } from '../api.js';
import { useToast } from '../components/Toast.jsx';
import Voltar from '../components/Voltar.jsx';
import { Alerta, Cabecalho, Carregando, Estrelas, Selo, SeloTicket } from '../components/ui.jsx';
import { useAuth } from '../auth.jsx';
import { useCarga } from '../hooks.js';
import { curto, dataHora, sla } from '../lib.js';

function AvaliarAtendimento({ ticketId }) {
  const toast = useToast();
  const [nota, setNota] = useState(0);
  const [feito, setFeito] = useState(false);
  const [erro, setErro] = useState('');
  async function enviar(e) {
    e.preventDefault();
    if (!nota) return setErro('Escolha uma nota de 1 a 5.');
    try {
      await api('/feedback', { method: 'POST', body: { target: 'ATENDIMENTO', nota, ticket_id: ticketId, comentario: new FormData(e.target).get('comentario') || null } });
      setFeito(true);
      toast.ok('Avaliação registrada. Obrigado!');
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
  const toast = useToast();
  const [enviando, setEnviando] = useState(false);
  const fim = useRef(null);
  const total = t?.messages?.length ?? 0;
  const aberto = t && t.status !== 'RESOLVIDO';

  // Como num chat: atualiza sozinho a cada 8 s enquanto o chamado está aberto e rola até a última mensagem.
  useEffect(() => {
    if (!aberto) return undefined;
    const timer = setInterval(() => { if (!document.hidden) recarregar({ silencioso: true }); }, 8000);
    return () => clearInterval(timer);
  }, [aberto, id]);
  useEffect(() => { fim.current?.scrollIntoView?.({ block: 'end', behavior: 'smooth' }); }, [total]);

  async function responder(e) {
    e.preventDefault();
    const form = e.target;
    setMsgErro('');
    setEnviando(true);
    try {
      await api(`/tickets/${id}/messages`, { method: 'POST', body: { mensagem: new FormData(form).get('mensagem') } });
      form.reset();
      toast.ok('Resposta enviada.');
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
      toast.ok(novo === 'RESOLVIDO' ? 'Chamado marcado como resolvido.' : 'Status atualizado.');
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
      <Voltar para="/chamados" />
      <Cabecalho titulo={t.assunto} subtitulo={`Chamado #${curto(t.id)} · ${t.categoria} · prioridade ${t.prioridade.toLowerCase()}`}
        acao={<div className="acoes"><SeloTicket status={t.status} /><Selo tom={s.tom}>{s.texto}</Selo></div>} />
      {t.order_id && <p><Link to={`/pedidos/${t.order_id}`}>Ver pedido #{curto(t.order_id)}</Link></p>}

      <section className="conversa" aria-label="Mensagens">
        {t.messages.map((m, i) => {
          const tipo = m.author_role === 'sistema' ? 'sistema' : m.author_role === 'cliente' ? 'cliente' : 'equipe';
          const nome = { sistema: 'Assistente automático', cliente: 'Cliente', equipe: 'Atendimento' }[tipo];
          return (
            <article key={m.id ?? i} className={`mensagem ${tipo}`}>
              <header><b>{nome}</b> · <time>{dataHora(m.created_at)}</time></header>
              <p>{m.mensagem}</p>
            </article>
          );
        })}
        <div ref={fim} />
      </section>

      {t.status !== 'RESOLVIDO' ? (
        <form className="cartao" onSubmit={responder}>
          <label className="campo"><span>Responder</span>
            <textarea name="mensagem" rows={3} required placeholder="Escreva sua mensagem… (Enter envia, Shift+Enter quebra a linha)"
              onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); e.target.form.requestSubmit(); } }} /></label>
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
