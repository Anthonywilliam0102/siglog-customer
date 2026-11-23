import { useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api.js';
import { Alerta, Cabecalho, Carregando, Vazio } from '../components/ui.jsx';
import { TabelaTickets } from './Chamados.jsx';
import { useCarga } from '../hooks.js';
import { sla } from '../lib.js';

// Visão da equipe: fila de chamados priorizada por SLA.
export default function Atendimento() {
  const [soAbertos, setSoAbertos] = useState(true);
  const { dados, erro, carregando } = useCarga(() => api('/tickets?limit=100'), []);
  const lista = (dados ?? []).filter((t) => !soAbertos || t.status !== 'RESOLVIDO')
    .sort((a, b) => new Date(a.sla_due_at) - new Date(b.sla_due_at));
  const vencidos = lista.filter((t) => sla(t).tom === 'erro').length;

  return (
    <div className="pagina">
      <Cabecalho titulo="Fila de atendimento" subtitulo="Chamados ordenados pelo prazo mais próximo."
        acao={<Link className="botao" to="/pedidos">Ver pedidos</Link>} />
      <div className="resumo">
        <div className="cartao"><p className="numero">{lista.length}</p><p className="muted">{soAbertos ? 'chamados abertos' : 'chamados'}</p></div>
        <div className="cartao"><p className={`numero ${vencidos ? 'alerta-texto' : ''}`}>{vencidos}</p><p className="muted">com SLA vencido</p></div>
      </div>
      <div className="filtros">
        <label><input type="checkbox" checked={soAbertos} onChange={(e) => setSoAbertos(e.target.checked)} /> Mostrar só os não resolvidos</label>
      </div>
      <Alerta>{erro}</Alerta>
      {carregando ? <Carregando /> : !lista.length ? <Vazio>Nenhum chamado na fila.</Vazio> : <TabelaTickets tickets={lista} />}
    </div>
  );
}
