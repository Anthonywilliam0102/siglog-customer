import { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { api } from '../api.js';
import { Alerta, Cabecalho, Campo } from '../components/ui.jsx';
import SeletorCliente, { useClienteId } from '../components/SeletorCliente.jsx';
import { useCarga } from '../hooks.js';
import { CATEGORIAS, curto, PRIORIDADES } from '../lib.js';

export default function NovoChamado() {
  const nav = useNavigate();
  const [params] = useSearchParams();
  const [escolhido, setEscolhido] = useState('');
  const clienteId = useClienteId(escolhido);
  const [pedido, setPedido] = useState(params.get('pedido') ?? '');
  const [erro, setErro] = useState('');
  const [ocupado, setOcupado] = useState(false);
  const pedidos = useCarga(() => (clienteId ? api(`/orders?limit=100&customer_id=${clienteId}`) : []), [clienteId]);

  async function enviar(e) {
    e.preventDefault();
    const f = Object.fromEntries(new FormData(e.target));
    setErro('');
    setOcupado(true);
    try {
      const t = await api('/tickets', {
        method: 'POST',
        body: { customer_id: clienteId, order_id: pedido || null, categoria: f.categoria, prioridade: f.prioridade, assunto: f.assunto, mensagem: f.mensagem },
      });
      nav(`/chamados/${t.id}`);
    } catch (err) {
      setErro(err.message);
      setOcupado(false);
    }
  }

  return (
    <div className="pagina estreita">
      <Cabecalho titulo="Abrir chamado" subtitulo="Conte o que aconteceu. Respondemos dentro do prazo da prioridade escolhida." />
      <form className="cartao" onSubmit={enviar}>
        <SeletorCliente valor={escolhido} onChange={setEscolhido} />
        <div className="duas">
          <Campo label="Categoria">
            <select name="categoria" required>{CATEGORIAS.map((c) => <option key={c}>{c}</option>)}</select>
          </Campo>
          <Campo label="Prioridade">
            <select name="prioridade" defaultValue="MEDIA">{Object.entries(PRIORIDADES).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select>
          </Campo>
        </div>
        <Campo label="Pedido relacionado (opcional)">
          <select value={pedido} onChange={(e) => setPedido(e.target.value)}>
            <option value="">Nenhum</option>
            {(pedidos.dados ?? []).map((p) => <option key={p.id} value={p.id}>#{curto(p.id)} · {p.origem} → {p.destino}</option>)}
          </select>
        </Campo>
        <Campo label="Assunto"><input name="assunto" required minLength={3} maxLength={200} /></Campo>
        <Campo label="Mensagem"><textarea name="mensagem" rows={5} required /></Campo>
        <Alerta>{erro}</Alerta>
        <button className="primario" disabled={ocupado || !clienteId}>{ocupado ? 'Enviando…' : 'Enviar chamado'}</button>
      </form>
    </div>
  );
}
