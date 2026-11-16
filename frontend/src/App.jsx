import { useState } from 'react';
import { api } from './api.js';

// Esqueleto do portal: Front/UI-UX evoluem a partir daqui conforme o protótipo do Figma.
// O token JWT vem do login (Supabase Auth) — por enquanto colado manualmente em desenvolvimento.
export default function App() {
  const [token, setToken] = useState('');
  const [customerId, setCustomerId] = useState('');
  const [quote, setQuote] = useState(null);
  const [msg, setMsg] = useState('');

  const run = async (fn) => {
    setMsg('');
    try { await fn(); } catch (e) { setMsg(e.message); }
  };

  const cotar = (e) => {
    e.preventDefault();
    const f = new FormData(e.target);
    run(async () => setQuote(await api('/quotes', {
      method: 'POST', token,
      body: { customer_id: customerId, origem: f.get('origem'), destino: f.get('destino'),
              peso_kg: Number(f.get('peso')), volume_m3: Number(f.get('volume')) },
    })));
  };

  const pedir = () => run(async () => {
    const o = await api('/orders', { method: 'POST', token, body: { quote_id: quote.id } });
    setMsg(`Pedido criado: ${o.id}`);
  });

  return (
    <main style={{ maxWidth: 640, margin: '2rem auto', fontFamily: 'system-ui, sans-serif', padding: '0 1rem' }}>
      <h1>SIG-Log Customer</h1>
      <p>Portal do Cliente — cotação e pedido (esqueleto).</p>

      <label>Token (dev)<input value={token} onChange={(e) => setToken(e.target.value)} style={{ width: '100%' }} /></label>
      <label>ID do cliente<input value={customerId} onChange={(e) => setCustomerId(e.target.value)} style={{ width: '100%' }} /></label>

      <h2>Solicitar cotação</h2>
      <form onSubmit={cotar} style={{ display: 'grid', gap: 8 }}>
        <input name="origem" placeholder="Origem" required />
        <input name="destino" placeholder="Destino" required />
        <input name="peso" type="number" step="0.1" placeholder="Peso (kg)" required />
        <input name="volume" type="number" step="0.01" placeholder="Volume (m³)" required />
        <button type="submit">Cotar</button>
      </form>

      {quote && (
        <section>
          <p>Valor estimado: <strong>R$ {quote.valor_estimado}</strong> (válida até {new Date(quote.expires_at).toLocaleString('pt-BR')})</p>
          <button onClick={pedir}>Criar pedido</button>
        </section>
      )}
      {msg && <p role="alert">{msg}</p>}
    </main>
  );
}
