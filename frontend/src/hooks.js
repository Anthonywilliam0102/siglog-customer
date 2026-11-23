import { useCallback, useEffect, useState } from 'react';

// Carrega dados assíncronos: { dados, erro, carregando, recarregar }.
export function useCarga(fn, deps = []) {
  const [s, setS] = useState({ dados: null, erro: '', carregando: true });
  const executar = useCallback(async () => {
    setS((a) => ({ ...a, carregando: true, erro: '' }));
    try {
      setS({ dados: await fn(), erro: '', carregando: false });
    } catch (e) {
      setS({ dados: null, erro: e.message, carregando: false });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  useEffect(() => { executar(); }, [executar]);
  return { ...s, recarregar: executar };
}
