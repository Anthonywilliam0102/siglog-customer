import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { api } from './api.js';
import { dadosDoLogin, getToken, supabase } from './session.js';

const Ctx = createContext(null);
export const useAuth = () => useContext(Ctx);

const STAFF = ['atendente', 'gestor'];

export function AuthProvider({ children }) {
  const [estado, setEstado] = useState({ carregando: true, perfil: null, clientes: [], login: null });

  const carregar = useCallback(async () => {
    if (!(await getToken())) return setEstado({ carregando: false, perfil: null, clientes: [], login: null });
    try {
      const perfil = await api('/me');
      const clientes = await api('/customers?limit=100');
      const login = await dadosDoLogin().catch(() => null);
      setEstado({ carregando: false, perfil, clientes, login });
    } catch {
      setEstado({ carregando: false, perfil: null, clientes: [], login: null });
    }
  }, []);

  useEffect(() => {
    carregar();
    window.addEventListener('siglog:sessao', carregar);
    const sub = supabase?.auth.onAuthStateChange(() => carregar());
    return () => {
      window.removeEventListener('siglog:sessao', carregar);
      sub?.data.subscription.unsubscribe();
    };
  }, [carregar]);

  const valor = useMemo(() => ({
    ...estado,
    equipe: STAFF.includes(estado.perfil?.role),
    // Perfil cliente: o próprio cadastro. A equipe não tem cadastro de cliente (a lista `clientes` é de todos os clientes).
    cliente: STAFF.includes(estado.perfil?.role) ? null : (estado.clientes[0] ?? null),
    recarregar: carregar,
  }), [estado, carregar]);

  return <Ctx.Provider value={valor}>{children}</Ctx.Provider>;
}
