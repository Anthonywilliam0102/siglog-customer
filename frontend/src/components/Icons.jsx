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

// Marcas dos provedores de login (ícones oficiais simplificados).
export function IconeProvedor({ provedor, tamanho = 18 }) {
  if (provedor === 'github') {
    return (
      <svg width={tamanho} height={tamanho} viewBox="0 0 16 16" aria-hidden="true" focusable="false" fill="currentColor">
        <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z" />
      </svg>
    );
  }
  return (
    <svg width={tamanho} height={tamanho} viewBox="0 0 18 18" aria-hidden="true" focusable="false">
      <path fill="#4285F4" d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844a4.14 4.14 0 01-1.796 2.716v2.259h2.908c1.702-1.567 2.684-3.875 2.684-6.615z" />
      <path fill="#34A853" d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 009 18z" />
      <path fill="#FBBC05" d="M3.964 10.71A5.41 5.41 0 013.682 9c0-.593.102-1.17.282-1.71V4.958H.957A8.996 8.996 0 000 9c0 1.452.348 2.827.957 4.042l3.007-2.332z" />
      <path fill="#EA4335" d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 00.957 4.958L3.964 7.29C4.672 5.163 6.656 3.58 9 3.58z" />
    </svg>
  );
}
