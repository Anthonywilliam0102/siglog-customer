import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../auth.jsx';
import { sair } from '../session.js';
import Icon from './Icons.jsx';

function iniciais(nome, email, papel) {
  const base = (nome || '').trim();
  if (base) return base.split(/\s+/).slice(0, 2).map((p) => p[0]).join('').toUpperCase();
  if (email) return email[0].toUpperCase();
  return papel[0].toUpperCase();
}

// Bolinha do usuário (foto do GitHub/Google ou iniciais) que abre o menu da conta, como nos sites em geral:
// atalhos do usuário no meio e "Sair da conta" no final.
export default function MenuUsuario() {
  const { perfil, equipe, cliente, login } = useAuth();
  const [aberto, setAberto] = useState(false);
  const [fotoFalhou, setFotoFalhou] = useState(false);
  const raiz = useRef(null);
  const botao = useRef(null);

  useEffect(() => {
    if (!aberto) return undefined;
    const fora = (e) => { if (raiz.current && !raiz.current.contains(e.target)) setAberto(false); };
    const tecla = (e) => { if (e.key === 'Escape') { setAberto(false); botao.current?.focus(); } };
    document.addEventListener('mousedown', fora);
    document.addEventListener('keydown', tecla);
    return () => { document.removeEventListener('mousedown', fora); document.removeEventListener('keydown', tecla); };
  }, [aberto]);

  const nome = cliente?.nome || login?.nome || (equipe ? 'Equipe SIG-Log' : 'Minha conta');
  const email = cliente?.email || login?.email || `perfil ${perfil.role}`;
  const papel = equipe ? perfil.role : 'cliente';
  const foto = login?.avatar && !fotoFalhou ? login.avatar : null;
  const sigla = iniciais(cliente?.nome || login?.nome, cliente?.email || login?.email, papel);

  const Bolinha = ({ grande = false }) => (
    <span className={`bolinha ${grande ? 'grande' : ''}`}>
      {foto ? <img src={foto} alt="" referrerPolicy="no-referrer" onError={() => setFotoFalhou(true)} /> : <span aria-hidden="true">{sigla}</span>}
    </span>
  );

  const grupos = [
    ['Minha área', [
      ['/pedidos', equipe ? 'Pedidos' : 'Meus pedidos', 'box'],
      ['/chamados', equipe ? 'Chamados' : 'Meus chamados', 'chat'],
      ['/sinistros', equipe ? 'Sinistros' : 'Meus sinistros', 'alert'],
    ]],
    ['Conta', [
      ['/conta', 'Minha conta', 'user'],
      ['/integracoes', 'Integrações', 'plug'],
      ...(equipe ? [['/configuracoes', 'Configurações', 'sliders']] : []),
    ]],
  ];

  return (
    <div className="menu-usuario" ref={raiz}>
      <button ref={botao} type="button" className="avatar" aria-haspopup="menu" aria-expanded={aberto} aria-label={`Menu da conta de ${nome}`}
        title={nome} onClick={() => setAberto((a) => !a)}>
        <Bolinha />
      </button>
      {aberto && (
        <div className="menu" role="menu" aria-label="Menu da conta">
          <div className="menu-cabeca">
            <Bolinha grande />
            <div>
              <b>{nome}</b>
              <span className="muted">{email}</span>
              <span className="selo ok">{papel}</span>
            </div>
          </div>
          {grupos.map(([titulo, itens]) => (
            <div key={titulo} className="menu-grupo" role="group" aria-label={titulo}>
              <p className="menu-titulo">{titulo}</p>
              {itens.map(([to, rotulo, icone]) => (
                <Link key={to} to={to} role="menuitem" className="menu-item" onClick={() => setAberto(false)}>
                  <Icon nome={icone} tamanho={18} /> {rotulo}
                </Link>
              ))}
            </div>
          ))}
          <div className="menu-grupo menu-final">
            <button type="button" role="menuitem" className="menu-item menu-sair" onClick={() => { setAberto(false); sair(); }}>
              <Icon nome="logout" tamanho={18} /> Sair da conta
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
