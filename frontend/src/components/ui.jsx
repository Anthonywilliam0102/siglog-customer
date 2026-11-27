import { STATUS_PEDIDO, STATUS_TICKET } from '../lib.js';

export const Alerta = ({ tipo = 'erro', children }) =>
  children ? <div className={`alerta ${tipo}`} role={tipo === 'erro' ? 'alert' : 'status'}>{children}</div> : null;

export const Selo = ({ tom = 'info', children }) => <span className={`selo ${tom}`}>{children}</span>;
export const SeloPedido = ({ status }) => <Selo tom={STATUS_PEDIDO[status]?.tom}>{STATUS_PEDIDO[status]?.label ?? status}</Selo>;
export const SeloTicket = ({ status }) => <Selo tom={STATUS_TICKET[status]?.tom}>{STATUS_TICKET[status]?.label ?? status}</Selo>;

export const Carregando = ({ texto = 'Carregando…' }) => <p className="muted" aria-busy="true">{texto}</p>;
export const Vazio = ({ children }) => <div className="vazio">{children}</div>;

export function Campo({ label, ajuda, children }) {
  return (
    <label className="campo">
      <span>{label}</span>
      {children}
      {ajuda && <small>{ajuda}</small>}
    </label>
  );
}

export function Cabecalho({ titulo, subtitulo, acao }) {
  return (
    <div className="cabecalho">
      <div>
        <h1>{titulo}</h1>
        {subtitulo && <p className="muted">{subtitulo}</p>}
      </div>
      {acao}
    </div>
  );
}

export const Estrelas = ({ valor, onChange }) => (
  <div className="estrelas" role="radiogroup" aria-label="Nota de 1 a 5">
    {[1, 2, 3, 4, 5].map((n) => (
      <button key={n} type="button" role="radio" aria-checked={valor === n} aria-label={`${n} de 5`}
        className={n <= valor ? 'on' : ''} onClick={() => onChange(n)}>★</button>
    ))}
  </div>
);
