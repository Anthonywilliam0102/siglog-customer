import { useAuth } from '../auth.jsx';
import { Campo } from './ui.jsx';

// Cliente: usa o próprio cadastro. Equipe: escolhe o cliente atendido.
export function useClienteId(escolhido) {
  const { equipe, cliente } = useAuth();
  return equipe ? escolhido : cliente?.id;
}

export default function SeletorCliente({ valor, onChange }) {
  const { equipe, clientes } = useAuth();
  if (!equipe) return null;
  return (
    <Campo label="Cliente atendido">
      <select value={valor} onChange={(e) => onChange(e.target.value)} required>
        <option value="">Selecione…</option>
        {clientes.map((c) => <option key={c.id} value={c.id}>{c.nome}</option>)}
      </select>
    </Campo>
  );
}
