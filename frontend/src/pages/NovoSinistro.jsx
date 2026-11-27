import { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { api } from '../api.js';
import { Alerta, Cabecalho, Campo, Carregando } from '../components/ui.jsx';
import { useCarga } from '../hooks.js';
import { curto, TIPOS_SINISTRO } from '../lib.js';

export default function NovoSinistro() {
  const nav = useNavigate();
  const [params] = useSearchParams();
  const [pedido, setPedido] = useState(params.get('pedido') ?? '');
  const [erro, setErro] = useState('');
  const [ocupado, setOcupado] = useState(false);
  const pedidos = useCarga(() => api('/orders?limit=100'), []);

  async function enviar(e) {
    e.preventDefault();
    const f = Object.fromEntries(new FormData(e.target));
    setErro('');
    setOcupado(true);
    try {
      await api('/claims', { method: 'POST', body: { order_id: pedido, tipo: f.tipo, descricao: f.descricao, valor_reclamado: f.valor } });
      nav('/sinistros');
    } catch (err) {
      setErro(err.message);
      setOcupado(false);
    }
  }

  const elegiveis = (pedidos.dados ?? []).filter((p) => p.status !== 'CANCELADO');
  return (
    <div className="pagina estreita">
      <Cabecalho titulo="Registrar sinistro" subtitulo="Informe o pedido afetado e o que aconteceu com a carga." />
      {pedidos.carregando ? <Carregando /> : (
        <form className="cartao" onSubmit={enviar}>
          <Campo label="Pedido">
            <select value={pedido} onChange={(e) => setPedido(e.target.value)} required>
              <option value="">Selecione…</option>
              {elegiveis.map((p) => <option key={p.id} value={p.id}>#{curto(p.id)} · {p.origem} → {p.destino}</option>)}
            </select>
          </Campo>
          <div className="duas">
            <Campo label="Tipo"><select name="tipo" required>{TIPOS_SINISTRO.map((t) => <option key={t}>{t}</option>)}</select></Campo>
            <Campo label="Valor reclamado (R$)"><input name="valor" type="number" min="0" step="0.01" required /></Campo>
          </div>
          <Campo label="Descrição" ajuda="Descreva o dano ou a ocorrência."><textarea name="descricao" rows={4} required minLength={3} /></Campo>
          <Alerta>{erro}</Alerta>
          <button className="primario" disabled={ocupado}>{ocupado ? 'Registrando…' : 'Registrar sinistro'}</button>
        </form>
      )}
    </div>
  );
}
