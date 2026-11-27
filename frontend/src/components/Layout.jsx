import { Link, NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../auth.jsx';
import { sair, temDemo } from '../session.js';
import Icon, { Logo } from './Icons.jsx';
import { useArrastar } from './Rolavel.jsx';
import SeloEquipe from './SeloEquipe.jsx';

export default function Layout() {
  const { perfil, equipe } = useAuth();
  const navRef = useArrastar();
  const itens = [
    ['/', 'Início', 'home'],
    ...(equipe ? [['/atendimento', 'Atendimento', 'shield']] : [['/cotacao', 'Nova cotação', 'calc']]),
    ['/pedidos', 'Pedidos', 'box'],
    ['/chamados', 'Chamados', 'chat'],
    ['/sinistros', 'Sinistros', 'alert'],
    ...(equipe ? [['/configuracoes', 'Configurações', 'sliders']] : []),
  ];
  return (
    <>
      <a className="pular" href="#conteudo">Pular para o conteúdo</a>
      {temDemo && <div className="faixa-demo" role="note">Modo demonstração: os dados são fictícios e ficam só no seu navegador. Este não é o sistema em produção.</div>}
      <header className="topo">
        <Link to="/" className="marca" aria-label="SIG-Log Customer — início"><Logo /> <span>SIG-Log <b>Customer</b></span></Link>
        <nav aria-label="Principal" ref={navRef}>
          {itens.map(([to, nome, icone]) => (
            <NavLink key={to} to={to} end={to === '/'}><Icon nome={icone} tamanho={17} /><span>{nome}</span></NavLink>
          ))}
        </nav>
        <div className="usuario">
          <span className="muted">{equipe ? perfil.role : 'cliente'}</span>
          <button className="link" onClick={sair}>Sair</button>
        </div>
      </header>
      <main id="conteudo"><Outlet /></main>
      <footer className="rodape"><SeloEquipe /></footer>
    </>
  );
}
