// Ilustração abstrata de uma rota entre centros de distribuição (decorativa).
export default function RouteArt({ className = '' }) {
  return (
    <svg className={`rota-arte ${className}`} viewBox="0 0 520 360" role="img" aria-label="Ilustração de uma rota logística entre quatro pontos" focusable="false">
      <defs>
        <linearGradient id="rg" x1="0" x2="1">
          <stop offset="0" stopColor="#2dd4a7" stopOpacity=".1" />
          <stop offset=".5" stopColor="#2dd4a7" />
          <stop offset="1" stopColor="#7fe9ff" />
        </linearGradient>
        <radialGradient id="glow"><stop offset="0" stopColor="#2dd4a7" stopOpacity=".55" /><stop offset="1" stopColor="#2dd4a7" stopOpacity="0" /></radialGradient>
      </defs>
      <g stroke="currentColor" strokeOpacity=".08" strokeWidth="1">
        {Array.from({ length: 9 }, (_, i) => <line key={`h${i}`} x1="0" x2="520" y1={20 + i * 40} y2={20 + i * 40} />)}
        {Array.from({ length: 14 }, (_, i) => <line key={`v${i}`} y1="0" y2="360" x1={20 + i * 40} x2={20 + i * 40} />)}
      </g>
      <path className="rota-linha" d="M60 290 C 130 290, 150 170, 230 170 C 310 170, 340 250, 400 150 C 430 100, 450 82, 470 70" fill="none" stroke="url(#rg)" strokeWidth="3.5" strokeLinecap="round" strokeDasharray="2 9" />
      {[[60, 290, 'CD'], [230, 170, 'Hub'], [400, 150, 'Hub'], [470, 70, 'Destino']].map(([x, y, t], i) => (
        <g key={i} className="rota-no" style={{ animationDelay: `${i * 0.5}s` }}>
          <circle cx={x} cy={y} r="26" fill="url(#glow)" />
          <circle cx={x} cy={y} r="9" fill="#0f1b33" stroke="#2dd4a7" strokeWidth="3" />
          <text x={x} y={y + 30} textAnchor="middle" fontSize="12" fontWeight="600" fill="currentColor" fillOpacity=".7">{t}</text>
        </g>
      ))}
    </svg>
  );
}
