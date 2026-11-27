import { createContext, useCallback, useContext, useMemo, useState } from 'react';
import Icon from './Icons.jsx';

const Ctx = createContext({ ok: () => {}, erro: () => {}, info: () => {} });
export const useToast = () => useContext(Ctx);

// Avisos curtos no canto da tela (somem sozinhos; leitores de tela anunciam via aria-live).
export function ToastProvider({ children }) {
  const [itens, setItens] = useState([]);
  const fechar = useCallback((id) => setItens((l) => l.filter((t) => t.id !== id)), []);
  const mostrar = useCallback((tipo, texto) => {
    const id = Math.random().toString(36).slice(2);
    setItens((l) => [...l.slice(-3), { id, tipo, texto }]);
    setTimeout(() => fechar(id), tipo === 'erro' ? 6500 : 4000);
  }, [fechar]);
  const api = useMemo(() => ({ ok: (t) => mostrar('ok', t), erro: (t) => mostrar('erro', t), info: (t) => mostrar('info', t) }), [mostrar]);
  return (
    <Ctx.Provider value={api}>
      {children}
      <div className="toasts" role="status" aria-live="polite">
        {itens.map((t) => (
          <div key={t.id} className={`toast ${t.tipo}`}>
            <Icon nome={t.tipo === 'erro' ? 'alert' : t.tipo === 'ok' ? 'check' : 'info'} tamanho={18} />
            <span>{t.texto}</span>
            <button type="button" className="toast-x" aria-label="Fechar aviso" onClick={() => fechar(t.id)}><Icon nome="x" tamanho={14} /></button>
          </div>
        ))}
      </div>
    </Ctx.Provider>
  );
}
