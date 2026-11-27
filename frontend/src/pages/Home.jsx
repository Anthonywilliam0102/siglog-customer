import { Link } from 'react-router-dom';
import { api } from '../api.js';
import { TabelaWrap } from '../components/Rolavel.jsx';
import { Alerta, Carregando, SeloPedido, Vazio } from '../components/ui.jsx';
import Icon from '../components/Icons.jsx';
import RouteArt from '../components/RouteArt.jsx';
import { useAuth } from '../auth.jsx';
import { useCarga } from '../hooks.js';
import { brl, curto, dataHora, sla } from '../lib.js';

const EM_ANDAMENTO = ['CRIADO', 'EM_SEPARACAO', 'EM_TRANSPORTE'];

function Stat({ icone, numero, rotulo, tom = '' }) {
  return (
    <div className={`stat vidro ${tom}`}>
      <span className="icone"><Icon nome={icone} /></span>
      <div><p className="numero">{numero}</p><p className="muted">{rotulo}</p></div>
    </div>
  );
}

function Atalho({ to, icone, titulo, sub }) {
  return (
    <Link className="atalho" to={to}>
      <span className="icone"><Icon nome={icone} /></span>
      <b>{titulo}</b>
      <span className="sub">{sub}</span>
      <span className="seta"><Icon nome="arrow" tamanho={18} /></span>
    </Link>
  );
}

export default function Home() {
  const { cliente, equipe, perfil } = useAuth();
  const pedidos = useCarga(() => api('/orders?limit=100'), []);
  const tickets = useCarga(() => api('/tickets?limit=100'), []);
  const lista = pedidos.dados ?? [];
  const abertos = (tickets.dados ?? []).filter((t) => t.status !== 'RESOLVIDO');
  const vencidos = abertos.filter((t) => sla(t).tom === 'erro').length;
  const andamento = lista.filter((p) => EM_ANDAMENTO.includes(p.status)).length;
  const entregues = lista.filter((p) => p.status === 'ENTREGUE').length;
  const nome = cliente?.nome?.split(' ')[0] ?? 'cliente';

  return (
    <div className="pagina">
      <section className="hero vidro" aria-label="Boas-vindas">
        <div>
          <p className="eyebrow">{equipe ? 'Equipe SIG-Log' : 'Portal do cliente'}</p>
          <h1>{equipe ? 'Painel da equipe' : `Olá, ${nome}`}</h1>
          <p className="lead">
            {equipe
              ? `Acompanhe a fila de atendimento e os pedidos de todos os clientes. Perfil: ${perfil.role}.`
              : 'Cote um frete, acompanhe seus pedidos e fale com o atendimento em um só lugar.'}
          </p>
          <div className="acoes">
            {equipe
              ? <Link className="botao primario" to="/atendimento">Abrir fila de atendimento</Link>
              : <Link className="botao primario" to="/cotacao">Nova cotação</Link>}
            <Link className="botao" to="/pedidos">Ver pedidos</Link>
          </div>
        </div>
        <RouteArt />
      </section>

      <Alerta>{pedidos.erro || tickets.erro}</Alerta>

      <section className="stats" aria-label="Resumo">
        <Stat icone="truck" numero={pedidos.carregando ? '–' : andamento} rotulo="pedidos em andamento" />
        <Stat icone="chat" numero={tickets.carregando ? '–' : abertos.length} rotulo="chamados abertos" />
        {equipe
          ? <Stat icone="alert" numero={tickets.carregando ? '–' : vencidos} rotulo="com SLA vencido" tom={vencidos ? 'erro' : ''} />
          : <Stat icone="check" numero={pedidos.carregando ? '–' : entregues} rotulo="pedidos entregues" />}
      </section>

      <div className="atalhos">
        {equipe
          ? <Atalho to="/atendimento" icone="shield" titulo="Fila de atendimento" sub={`${abertos.length} abertos · ${vencidos} com SLA vencido`} />
          : <Atalho to="/cotacao" icone="calc" titulo="Nova cotação" sub="Veja o valor e crie um pedido" />}
        <Atalho to="/pedidos" icone="box" titulo="Pedidos" sub="Status e rastreamento" />
        <Atalho to="/chamados/novo" icone="chat" titulo="Abrir chamado" sub="Fale com o SAC" />
        <Atalho to="/sinistros/novo" icone="alert" titulo="Registrar sinistro" sub="Avaria ou extravio" />
      </div>

      <section>
        <h2>Pedidos recentes</h2>
        {pedidos.carregando ? <Carregando /> : !lista.length ? (
          <Vazio icone="box">{equipe ? 'Nenhum pedido ainda.' : <>Você ainda não tem pedidos. <Link to="/cotacao">Faça sua primeira cotação</Link>.</>}</Vazio>
        ) : (
          <TabelaWrap>
            <table>
              <thead><tr><th>Pedido</th><th>Rota</th><th>Status</th><th>Valor</th><th>Criado em</th></tr></thead>
              <tbody>
                {lista.slice(0, 5).map((p) => (
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
      </section>
    </div>
  );
}
