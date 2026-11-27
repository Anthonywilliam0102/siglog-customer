import { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { Alerta } from '../components/ui.jsx';
import Icon, { Logo } from '../components/Icons.jsx';
import RouteArt from '../components/RouteArt.jsx';
import { useAuth } from '../auth.jsx';
import { entrar, entrarComTokenDev, entrarDemo, temDemo, temSupabase } from '../session.js';

// Atalhos só no modo de desenvolvimento (sem Supabase) e somente se as variáveis existirem no build local.
const RAPIDOS = [['Entrar como cliente', import.meta.env.VITE_DEV_TOKEN_CLIENTE], ['Entrar como atendente', import.meta.env.VITE_DEV_TOKEN_ATENDENTE]]
  .filter(([, t]) => t);

export default function Login() {
  const { perfil, carregando } = useAuth();
  const [erro, setErro] = useState(() => {
    try { const a = sessionStorage.getItem('siglog_aviso'); sessionStorage.removeItem('siglog_aviso'); return a || ''; } catch { return ''; }
  });
  const [enviando, setEnviando] = useState(false);
  if (!carregando && perfil) return <Navigate to="/" replace />;

  async function enviar(e) {
    e.preventDefault();
    const f = new FormData(e.target);
    setErro('');
    setEnviando(true);
    try {
      if (temSupabase) await entrar(f.get('email'), f.get('senha'));
      else entrarComTokenDev(f.get('token'));
    } catch (err) {
      setErro(err.message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <main className="login-pagina">
      <section className="login-marca" aria-label="Apresentação">
        <div className="marca"><Logo tamanho={34} /> <span>SIG-Log <b>Customer</b></span></div>
        <div>
          <h2>Sua carga, do pedido à <em>entrega</em>.</h2>
          <ul>
            <li><span className="icone"><Icon nome="calc" tamanho={18} /></span>Cotação em segundos, com validade clara</li>
            <li><span className="icone"><Icon nome="truck" tamanho={18} /></span>Acompanhe cada etapa do seu pedido</li>
            <li><span className="icone"><Icon nome="clock" tamanho={18} /></span>Atendimento com prazo de resposta (SLA) visível</li>
          </ul>
        </div>
        <RouteArt />
      </section>

      <section className="login-form">
        <form className="cartao vidro" onSubmit={enviar}>
          <div className="marca"><Logo /></div>
          <div>
            <h1>Entrar no portal</h1>
            <p className="muted">Use o e-mail e a senha do seu cadastro.</p>
          </div>
          {temDemo ? (
            <p className="alerta info">Modo demonstração: explore o portal com dados fictícios. Nada é enviado a nenhum servidor.</p>
          ) : temSupabase ? (
            <>
              <label className="campo"><span>E-mail</span><input name="email" type="email" autoComplete="username" placeholder="voce@empresa.com" required /></label>
              <label className="campo"><span>Senha</span><input name="senha" type="password" autoComplete="current-password" placeholder="Sua senha" required /></label>
            </>
          ) : (
            <label className="campo">
              <span>Token de desenvolvimento</span>
              <textarea name="token" rows={4} required placeholder="Cole o token gerado por scripts/gen_token.py" />
              <small>Supabase não configurado (VITE_SUPABASE_URL). Modo de desenvolvimento.</small>
            </label>
          )}
          <Alerta>{erro}</Alerta>
          {temDemo ? (
            <div className="acoes col-demo">
              <button type="button" className="primario" onClick={() => entrarDemo('cliente')}>Entrar como cliente (demonstração)</button>
              <button type="button" onClick={() => entrarDemo('atendente')}>Entrar como atendente (demonstração)</button>
            </div>
          ) : (
            <button className="primario" disabled={enviando}>{enviando ? 'Entrando…' : 'Entrar'}</button>
          )}
          {!temSupabase && !temDemo && RAPIDOS.length > 0 && (
            <div className="acoes">
              {RAPIDOS.map(([rotulo, t]) => <button type="button" key={rotulo} onClick={() => entrarComTokenDev(t)}>{rotulo}</button>)}
            </div>
          )}
          <p className="aviso-rodape">Projeto acadêmico · dados fictícios</p>
        </form>
      </section>
    </main>
  );
}
