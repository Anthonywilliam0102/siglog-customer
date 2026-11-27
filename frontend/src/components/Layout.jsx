import { Link, NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../auth.jsx';
import { sair, temDemo } from '../session.js';
import { Logo } from './Icons.jsx';

export default function Layout() {
  const { perfil, equipe } = useAuth();
  const itens = [
    ['/', 'Início'],
    ...(equipe ? [['/atendimento', 'Atendimento']] : [['/cotacao', 'Nova cotação']]),
    ['/pedidos', 'Pedidos'],
    ['/chamados', 'Chamados'],
    ['/sinistros', 'Sinistros'],
  ];
  return (
    <>
      <a className="pular" href="#conteudo">Pular para o conteúdo</a>
      {temDemo && <div className="faixa-demo" role="note">Modo demonstração: os dados são fictícios e ficam só no seu navegador. Este não é o sistema em produção.</div>}
      <header className="topo">
        <Link to="/" className="marca" aria-label="SIG-Log Customer — início"><Logo /> <span>SIG-Log <b>Customer</b></span></Link>
        <nav aria-label="Principal">
          {itens.map(([to, nome]) => (
            <NavLink key={to} to={to} end={to === '/'}>{nome}</NavLink>
          ))}
        </nav>
        <div className="usuario">
          <span className="muted">{equipe ? perfil.role : 'cliente'}</span>
          <button className="link" onClick={sair}>Sair</button>
        </div>
      </header>
      <main id="conteudo"><Outlet /></main>
    </>
  );
}
