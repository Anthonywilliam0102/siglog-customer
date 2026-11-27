import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api.js';
import { Alerta, Campo, Cabecalho } from '../components/ui.jsx';
import SeletorCliente, { useClienteId } from '../components/SeletorCliente.jsx';
import { brl, dataHora } from '../lib.js';

export default function Cotacao() {
  const nav = useNavigate();
  const [escolhido, setEscolhido] = useState('');
  const clienteId = useClienteId(escolhido);
  const [cotacao, setCotacao] = useState(null);
  const [erro, setErro] = useState('');
  const [ocupado, setOcupado] = useState(false);

  async function cotar(e) {
    e.preventDefault();
    const f = Object.fromEntries(new FormData(e.target));
    setErro('');
    setOcupado(true);
    try {
      setCotacao(await api('/quotes', {
        method: 'POST',
        body: { customer_id: clienteId, origem: f.origem, destino: f.destino, peso_kg: Number(f.peso), volume_m3: Number(f.volume) },
      }));
    } catch (err) {
      setErro(err.message);
    } finally {
      setOcupado(false);
    }
  }

  async function confirmar() {
    setErro('');
    setOcupado(true);
    try {
      const pedido = await api('/orders', { method: 'POST', body: { quote_id: cotacao.id } });
      nav(`/pedidos/${pedido.id}`);
    } catch (err) {
      setErro(err.message);
      setOcupado(false);
    }
  }

  return (
    <div className="pagina estreita">
      <Cabecalho titulo="Nova cotação" subtitulo="Informe a rota e a carga para ver o valor estimado." />
      {!cotacao ? (
        <form className="cartao" onSubmit={cotar}>
          <SeletorCliente valor={escolhido} onChange={setEscolhido} />
          <div className="duas">
            <Campo label="Origem"><input name="origem" required minLength={2} placeholder="São Paulo/SP" /></Campo>
            <Campo label="Destino"><input name="destino" required minLength={2} placeholder="Recife/PE" /></Campo>
          </div>
          <div className="duas">
            <Campo label="Peso (kg)"><input name="peso" type="number" min="0.1" max="100000" step="0.1" required /></Campo>
            <Campo label="Volume (m³)"><input name="volume" type="number" min="0.01" max="1000" step="0.01" required /></Campo>
          </div>
          <Alerta>{erro}</Alerta>
          <button className="primario" disabled={ocupado || !clienteId}>{ocupado ? 'Calculando…' : 'Calcular cotação'}</button>
        </form>
      ) : (
        <section className="cartao destaque" aria-live="polite">
          <p className="muted">{cotacao.origem} → {cotacao.destino} · {cotacao.peso_kg} kg · {cotacao.volume_m3} m³</p>
          <p className="valor">{brl(cotacao.valor_estimado)}</p>
          <p className="muted">Valor estimado. Válida até {dataHora(cotacao.expires_at)}.</p>
          <Alerta>{erro}</Alerta>
          <div className="acoes">
            <button className="primario" onClick={confirmar} disabled={ocupado}>{ocupado ? 'Criando…' : 'Confirmar pedido'}</button>
            <button onClick={() => setCotacao(null)} disabled={ocupado}>Refazer</button>
          </div>
        </section>
      )}
    </div>
  );
}
