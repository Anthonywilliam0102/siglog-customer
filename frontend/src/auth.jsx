import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { api } from './api.js';
import { getToken, supabase } from './session.js';

const Ctx = createContext(null);
export const useAuth = () => useContext(Ctx);

const STAFF = ['atendente', 'gestor'];

export function AuthProvider({ children }) {
  const [estado, setEstado] = useState({ carregando: true, perfil: null, clientes: [] });

  const carregar = useCallback(async () => {
    if (!(await getToken())) return setEstado({ carregando: false, perfil: null, clientes: [] });
    try {
      const perfil = await api('/me');
      const clientes = await api('/customers?limit=100');
      setEstado({ carregando: false, perfil, clientes });
    } catch {
      setEstado({ carregando: false, perfil: null, clientes: [] });
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
    cliente: estado.clientes[0] ?? null, // para o perfil cliente: o próprio cadastro
    recarregar: carregar,
  }), [estado, carregar]);

  return <Ctx.Provider value={valor}>{children}</Ctx.Provider>;
}
