import { Link } from 'react-router-dom';
import { api } from '../api.js';
import { Alerta, Cabecalho, Carregando, SeloPedido, Vazio } from '../components/ui.jsx';
import { useAuth } from '../auth.jsx';
import { useCarga } from '../hooks.js';
import { brl, curto, dataHora, sla } from '../lib.js';

export default function Home() {
  const { cliente, equipe, perfil } = useAuth();
  const pedidos = useCarga(() => api('/orders?limit=5'), []);
  const tickets = useCarga(() => api('/tickets?limit=100'), []);
  const abertos = (tickets.dados ?? []).filter((t) => t.status !== 'RESOLVIDO');
  const vencidos = abertos.filter((t) => sla(t).tom === 'erro').length;

  return (
    <div className="pagina">
      <Cabecalho titulo={equipe ? 'Painel da equipe' : `Olá, ${cliente?.nome?.split(' ')[0] ?? 'cliente'}`}
        subtitulo={equipe ? `Perfil: ${perfil.role}` : 'O que você quer fazer hoje?'} />
      <Alerta>{pedidos.erro || tickets.erro}</Alerta>

      <div className="atalhos">
        {equipe ? (
          <Link className="cartao atalho" to="/atendimento"><b>Fila de atendimento</b><span>{abertos.length} abertos · {vencidos} com SLA vencido</span></Link>
        ) : (
          <Link className="cartao atalho" to="/cotacao"><b>Nova cotação</b><span>Veja o valor e crie um pedido</span></Link>
        )}
        <Link className="cartao atalho" to="/pedidos"><b>Pedidos</b><span>Status e rastreamento</span></Link>
        <Link className="cartao atalho" to="/chamados/novo"><b>Abrir chamado</b><span>Fale com o SAC</span></Link>
        <Link className="cartao atalho" to="/sinistros/novo"><b>Registrar sinistro</b><span>Avaria ou extravio</span></Link>
      </div>

      <section>
        <h2>Pedidos recentes</h2>
        {pedidos.carregando ? <Carregando /> : !pedidos.dados?.length ? (
          <Vazio>{equipe ? 'Nenhum pedido ainda.' : <>Você ainda não tem pedidos. <Link to="/cotacao">Faça sua primeira cotação</Link>.</>}</Vazio>
        ) : (
          <div className="tabela-wrap">
            <table>
              <thead><tr><th>Pedido</th><th>Rota</th><th>Status</th><th>Valor</th><th>Criado em</th></tr></thead>
              <tbody>
                {pedidos.dados.map((p) => (
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
          </div>
        )}
      </section>
    </div>
  );
}
