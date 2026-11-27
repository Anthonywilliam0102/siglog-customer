import { useCallback, useEffect, useState } from 'react';

// Carrega dados assíncronos: { dados, erro, carregando, recarregar }.
export function useCarga(fn, deps = []) {
  const [s, setS] = useState({ dados: null, erro: '', carregando: true });
  const executar = useCallback(async (opcoes) => {
    const silencioso = opcoes?.silencioso === true;
    if (!silencioso) setS((a) => ({ ...a, carregando: true, erro: '' }));
    try {
      setS({ dados: await fn(), erro: '', carregando: false });
    } catch (e) {
      if (!silencioso) setS({ dados: null, erro: e.message, carregando: false }); // recarga silenciosa mantém o que já está na tela
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  useEffect(() => { executar(); }, [executar]);
  return { ...s, recarregar: executar };
}
