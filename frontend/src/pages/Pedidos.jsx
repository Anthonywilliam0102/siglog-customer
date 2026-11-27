import { useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api.js';
import { TabelaWrap } from '../components/Rolavel.jsx';
import { Alerta, Cabecalho, Carregando, SeloPedido, Vazio } from '../components/ui.jsx';
import { useAuth } from '../auth.jsx';
import { useCarga } from '../hooks.js';
import { brl, curto, dataHora, STATUS_PEDIDO } from '../lib.js';

export default function Pedidos() {
  const { equipe } = useAuth();
  const [status, setStatus] = useState('');
  const { dados, erro, carregando } = useCarga(() => api(`/orders?limit=100${status ? `&status=${status}` : ''}`), [status]);

  return (
    <div className="pagina">
      <Cabecalho titulo="Pedidos" subtitulo={equipe ? 'Todos os pedidos.' : 'Acompanhe seus pedidos.'}
        acao={!equipe && <Link className="botao primario" to="/cotacao">Nova cotação</Link>} />
      <div className="filtros">
        <label>Status{' '}
          <select value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="">Todos</option>
            {Object.entries(STATUS_PEDIDO).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
          </select>
        </label>
      </div>
      <Alerta>{erro}</Alerta>
      {carregando ? <Carregando /> : !dados?.length ? <Vazio>Nenhum pedido encontrado.</Vazio> : (
        <TabelaWrap>
          <table>
            <thead><tr><th>Pedido</th><th>Rota</th><th>Status</th><th>Valor</th><th>Criado em</th></tr></thead>
            <tbody>
              {dados.map((p) => (
                <tr key={p.id}>
                  <td><Link to={`/pedidos/${p.id}`}>#{curto(p.id)}</Link></td>
                  <td>{p.origem} → {p.destino}</td>
                  <td><SeloPedido status={p.status} /></td>
                  <td>{brl(p.valor_estimado)}</td>
                  <td>{dataHora(p.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </TabelaWrap>
      )}
    </div>
  );
}
