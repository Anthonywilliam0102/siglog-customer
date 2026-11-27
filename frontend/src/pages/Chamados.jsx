import { useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api.js';
import { Alerta, Cabecalho, Carregando, Selo, SeloTicket, Vazio } from '../components/ui.jsx';
import { useAuth } from '../auth.jsx';
import { useCarga } from '../hooks.js';
import { curto, dataHora, sla, STATUS_TICKET } from '../lib.js';

export function TabelaTickets({ tickets }) {
  return (
    <div className="tabela-wrap">
      <table>
        <thead><tr><th>Chamado</th><th>Assunto</th><th>Categoria</th><th>Status</th><th>Prazo (SLA)</th><th>Aberto em</th></tr></thead>
        <tbody>
          {tickets.map((t) => {
            const s = sla(t);
            return (
              <tr key={t.id}>
                <td><Link to={`/chamados/${t.id}`}>#{curto(t.id)}</Link></td>
                <td>{t.assunto}</td>
                <td>{t.categoria}</td>
                <td><SeloTicket status={t.status} /></td>
                <td><Selo tom={s.tom}>{s.texto}</Selo></td>
                <td>{dataHora(t.created_at)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export default function Chamados() {
  const { equipe } = useAuth();
  const [status, setStatus] = useState('');
  const { dados, erro, carregando } = useCarga(() => api(`/tickets?limit=100${status ? `&status=${status}` : ''}`), [status]);
  return (
    <div className="pagina">
      <Cabecalho titulo="Chamados" subtitulo={equipe ? 'Todos os chamados.' : 'Seus atendimentos com o SAC.'}
        acao={<Link className="botao primario" to="/chamados/novo">Abrir chamado</Link>} />
      <div className="filtros">
        <label>Status{' '}
          <select value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="">Todos</option>
            {Object.entries(STATUS_TICKET).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
          </select>
        </label>
      </div>
      <Alerta>{erro}</Alerta>
      {carregando ? <Carregando /> : !dados?.length ? <Vazio>Nenhum chamado encontrado.</Vazio> : <TabelaTickets tickets={dados} />}
    </div>
  );
}
