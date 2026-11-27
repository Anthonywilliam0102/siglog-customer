// Ícones em SVG inline (sem dependência). Traço herda `currentColor`.
const P = {
  box: 'M21 8l-9-5-9 5v8l9 5 9-5V8z M3 8l9 5 9-5 M12 13v8',
  truck: 'M3 6h11v10H3z M14 10h4l3 3v3h-7z',
  chat: 'M21 12a8 8 0 0 1-11.5 7.2L4 20l1-4.5A8 8 0 1 1 21 12z',
  alert: 'M12 3l10 18H2L12 3z M12 10v5 M12 18h.01',
  star: 'M12 3l2.7 5.6 6.3.9-4.5 4.4 1 6.2L12 17l-5.5 3.1 1-6.2L3 9.5l6.3-.9L12 3z',
  calc: 'M5 3h14v18H5z M8 7h8 M8 12h2 M12 12h2 M16 12h.01 M8 16h2 M12 16h2 M16 16h.01',
  check: 'M5 12l4 4 10-10',
  arrow: 'M5 12h14 M13 6l6 6-6 6',
  clock: 'M12 7v5l3 2',
  shield: 'M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3z',
  inbox: 'M4 13l2-8h12l2 8 M4 13v6h16v-6 M4 13h5l1 2h4l1-2h5',
  home: 'M3 11l9-8 9 8 M5 10v10h5v-6h4v6h5V10',
  sliders: 'M4 6h8 M16 6h4 M4 12h2 M10 12h10 M4 18h10 M18 18h2',
  back: 'M19 12H5 M11 6l-6 6 6 6',
  cap: 'M2 9l10-5 10 5-10 5-10-5z M6 11.5V16c0 1.5 3 3 6 3s6-1.5 6-3v-4.5 M22 9v6',
  key: 'M11 12l9-9 M16 7l3 3 M14 9l2 2',
  plug: 'M9 2v6 M15 2v6 M6 8h12v4a6 6 0 0 1-12 0V8z M12 18v4',
  info: 'M12 11v5 M12 8h.01',
  link: 'M14 4h6v6 M20 4l-9 9 M18 14v5H5V6h5',
  refresh: 'M20 11a8 8 0 0 0-14-4L4 9 M4 4v5h5 M4 13a8 8 0 0 0 14 4l2-2 M20 20v-5h-5',
  x: 'M6 6l12 12 M18 6L6 18',
};
const EXTRA = {
  sliders: [[14, 6, 2], [8, 12, 2], [16, 18, 2]],
  key: [[8, 15, 4]],
  info: [[12, 12, 9]],
  clock: [[12, 12, 9]],
  truck: [[7, 18, 2], [17, 18, 2]],
};

export default function Icon({ nome, tamanho = 22, ...resto }) {
  return (
    <svg width={tamanho} height={tamanho} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false" {...resto}>
      {P[nome].split(' M').map((d, i) => <path key={i} d={i ? `M${d}` : d} />)}
      {(EXTRA[nome] ?? []).map(([cx, cy, r], i) => <circle key={`c${i}`} cx={cx} cy={cy} r={r} />)}
    </svg>
  );
}

export function Logo({ tamanho = 30 }) {
  return (
    <svg width={tamanho} height={tamanho} viewBox="0 0 32 32" aria-hidden="true" focusable="false">
      <rect width="32" height="32" rx="9" fill="#0f1b33" />
      <rect x=".75" y=".75" width="30.5" height="30.5" rx="8.5" fill="none" stroke="rgba(255,255,255,.16)" strokeWidth="1.5" />
      <path d="M8 21c4 0 4-10 8-10s4 10 8 10" fill="none" stroke="#2dd4a7" strokeWidth="2.4" strokeLinecap="round" />
      <circle cx="8" cy="21" r="2.4" fill="#2dd4a7" />
      <circle cx="24" cy="21" r="2.4" fill="#2dd4a7" />
    </svg>
  );
}
