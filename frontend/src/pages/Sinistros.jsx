import { Link } from 'react-router-dom';
import { api } from '../api.js';
import { TabelaWrap } from '../components/Rolavel.jsx';
import { Alerta, Cabecalho, Carregando, Selo, Vazio } from '../components/ui.jsx';
import { useCarga } from '../hooks.js';
import { brl, curto, dataHora } from '../lib.js';

const TOM = { REGISTRADO: 'info', EM_ANALISE: 'aviso', APROVADO: 'ok', NEGADO: 'erro' };

export default function Sinistros() {
  const { dados, erro, carregando } = useCarga(() => api('/claims?limit=100'), []);
  return (
    <div className="pagina">
      <Cabecalho titulo="Sinistros" subtitulo="Avarias, extravios e ocorrências com a sua carga."
        acao={<Link className="botao primario" to="/sinistros/novo">Registrar sinistro</Link>} />
      <Alerta>{erro}</Alerta>
      {carregando ? <Carregando /> : !dados?.length ? <Vazio>Nenhum sinistro registrado.</Vazio> : (
        <TabelaWrap>
          <table>
            <thead><tr><th>Sinistro</th><th>Pedido</th><th>Tipo</th><th>Descrição</th><th>Valor</th><th>Status</th><th>Registrado em</th></tr></thead>
            <tbody>
              {dados.map((c) => (
                <tr key={c.id}>
                  <td>#{curto(c.id)}</td>
                  <td><Link to={`/pedidos/${c.order_id}`}>#{curto(c.order_id)}</Link></td>
                  <td>{c.tipo}</td>
                  <td>{c.descricao}</td>
                  <td>{brl(c.valor_reclamado)}</td>
                  <td><Selo tom={TOM[c.status] ?? 'info'}>{c.status.replace('_', ' ')}</Selo></td>
                  <td>{dataHora(c.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </TabelaWrap>
      )}
    </div>
  );
}
