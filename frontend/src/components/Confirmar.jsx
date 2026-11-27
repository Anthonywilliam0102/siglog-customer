import { useEffect, useRef } from 'react';

// Caixa de confirmação (usa <dialog>: foco preso e Esc para cancelar de graça).
export default function Confirmar({ aberto, titulo, texto, rotulo = 'Confirmar', perigo = false, onConfirmar, onCancelar }) {
  const ref = useRef(null);
  useEffect(() => {
    const d = ref.current;
    if (!d) return;
    if (aberto && !d.open) d.showModal();
    if (!aberto && d.open) d.close();
  }, [aberto]);
  return (
    <dialog ref={ref} className="modal" onClose={onCancelar} onClick={(e) => e.target === ref.current && onCancelar()}>
      <h2>{titulo}</h2>
      <p className="muted">{texto}</p>
      <div className="acoes">
        <button type="button" onClick={onCancelar}>Voltar</button>
        <button type="button" className={perigo ? 'perigo' : 'primario'} onClick={onConfirmar}>{rotulo}</button>
      </div>
    </dialog>
  );
}
