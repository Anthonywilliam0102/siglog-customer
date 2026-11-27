import { useEffect, useRef } from 'react';

// Contêiner rolável na horizontal que também aceita ARRASTAR com o mouse (tabelas largas, menus).
export function useArrastar() {
  const ref = useRef(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return undefined;
    let baixo = false, moveu = false, x0 = 0, s0 = 0;
    const down = (e) => {
      if (e.pointerType !== 'mouse' || e.button !== 0 || el.scrollWidth <= el.clientWidth) return;
      baixo = true; moveu = false; x0 = e.clientX; s0 = el.scrollLeft;
    };
    const move = (e) => {
      if (!baixo) return;
      const dx = e.clientX - x0;
      if (Math.abs(dx) > 5) { moveu = true; el.classList.add('arrastando'); el.scrollLeft = s0 - dx; }
    };
    const up = () => { baixo = false; el.classList.remove('arrastando'); };
    const click = (e) => { if (moveu) { e.preventDefault(); e.stopPropagation(); moveu = false; } };
    el.addEventListener('pointerdown', down);
    window.addEventListener('pointermove', move);
    window.addEventListener('pointerup', up);
    el.addEventListener('click', click, true);
    return () => {
      el.removeEventListener('pointerdown', down); window.removeEventListener('pointermove', move);
      window.removeEventListener('pointerup', up); el.removeEventListener('click', click, true);
    };
  }, []);
  return ref;
}

export function TabelaWrap({ children }) {
  const ref = useArrastar();
  return <div className="tabela-wrap" ref={ref}>{children}</div>;
}
