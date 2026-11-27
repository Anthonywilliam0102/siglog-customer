import { Link, NavLink, Outlet, useLocation, useMatch } from 'react-router-dom';
import { useAuth } from '../auth.jsx';
import { temDemo } from '../session.js';
import Icon, { Logo } from './Icons.jsx';
import { useArrastar } from './Rolavel.jsx';
import MenuUsuario from './MenuUsuario.jsx';
import SeloEquipe from './SeloEquipe.jsx';

export default function Layout() {
  const { perfil, equipe } = useAuth();
  const navRef = useArrastar();
  const { pathname } = useLocation();
  const noPedido = useMatch('/pedidos/:id');
  const mostrarChat = !pathname.startsWith('/chamados/novo') && !pathname.startsWith('/login') && !pathname.startsWith('/cadastro');
  const itens = [
    ['/', 'Início', 'home'],
    ...(equipe ? [['/atendimento', 'Atendimento', 'shield']] : [['/cotacao', 'Nova cotação', 'calc']]),
  ]; // pedidos, chamados, sinistros, conta e configurações ficam no menu da "carinha" (MenuUsuario)
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
          <MenuUsuario />
        </div>
      </header>
      <main id="conteudo"><Outlet /></main>
      {mostrarChat && (
        <Link className="fab-chat" to={`/chamados/novo${noPedido ? `?pedido=${noPedido.params.id}` : ''}`} aria-label="Fale conosco: abrir o chat de atendimento">
          <span className="fab-icone"><Icon nome="headset" tamanho={26} /></span>
          <span className="fab-texto">Fale conosco</span>
        </Link>
      )}
      <footer className="rodape"><SeloEquipe /></footer>
    </>
  );
}
