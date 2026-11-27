import { useId, useRef, useState } from 'react';

// Capitais do Brasil no formato "Cidade/UF" (o mesmo que a API recebe em origem e destino).
export const CAPITAIS = [
  'São Paulo/SP', 'Rio de Janeiro/RJ', 'Brasília/DF', 'Salvador/BA', 'Fortaleza/CE', 'Belo Horizonte/MG', 'Manaus/AM', 'Curitiba/PR',
  'Recife/PE', 'Goiânia/GO', 'Belém/PA', 'Porto Alegre/RS', 'São Luís/MA', 'Maceió/AL', 'Natal/RN', 'Teresina/PI', 'João Pessoa/PB',
  'Campo Grande/MS', 'Cuiabá/MT', 'Aracaju/SE', 'Florianópolis/SC', 'Vitória/ES', 'Porto Velho/RO', 'Macapá/AP', 'Rio Branco/AC',
  'Boa Vista/RR', 'Palmas/TO',
];

const sem = (t) => t.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();

// Campo com lista das principais capitais ao clicar; filtra enquanto digita e também aceita outra cidade (texto livre).
export default function CampoCidade({ name, placeholder, valorInicial = '' }) {
  const id = useId();
  const [valor, setValor] = useState(valorInicial);
  const [aberto, setAberto] = useState(false);
  const [ativo, setAtivo] = useState(-1);
  const raiz = useRef(null);
  const lista = CAPITAIS.filter((c) => sem(c).includes(sem(valor.trim())));

  function escolher(c) { setValor(c); setAberto(false); setAtivo(-1); }
  function tecla(e) {
    if (e.key === 'ArrowDown') { e.preventDefault(); setAberto(true); setAtivo((a) => Math.min(a + 1, lista.length - 1)); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); setAtivo((a) => Math.max(a - 1, 0)); }
    else if (e.key === 'Enter' && aberto && ativo >= 0 && lista[ativo]) { e.preventDefault(); escolher(lista[ativo]); }
    else if (e.key === 'Escape') setAberto(false);
  }

  return (
    <div className="combo" ref={raiz} onBlur={(e) => { if (!raiz.current.contains(e.relatedTarget)) setAberto(false); }}>
      <input name={name} required minLength={2} autoComplete="off" placeholder={placeholder} value={valor}
        role="combobox" aria-expanded={aberto} aria-controls={id} aria-autocomplete="list"
        onChange={(e) => { setValor(e.target.value); setAberto(true); setAtivo(-1); }} onFocus={() => setAberto(true)} onClick={() => setAberto(true)} onKeyDown={tecla} />
      {aberto && lista.length > 0 && (
        <ul className="combo-lista" id={id} role="listbox" aria-label="Principais capitais">
          {!valor.trim() && <li className="combo-titulo" role="presentation">Principais capitais</li>}
          {lista.map((c, i) => (
            <li key={c} role="option" aria-selected={i === ativo} className={i === ativo ? 'ativo' : ''} tabIndex={-1}
              onMouseDown={(e) => e.preventDefault()} onClick={() => escolher(c)}>{c}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
