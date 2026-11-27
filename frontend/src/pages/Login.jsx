import { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { Alerta } from '../components/ui.jsx';
import { Logo } from '../components/Icons.jsx';
import RouteArt from '../components/RouteArt.jsx';
import SeloEquipe from '../components/SeloEquipe.jsx';
import { useAuth } from '../auth.jsx';
import { criarConta, entrar, entrarComTokenDev, entrarDemo, temDemo, temSupabase } from '../session.js';

// Atalhos só no modo de desenvolvimento (sem Supabase) e somente se as variáveis existirem no build local.
const RAPIDOS = [['Entrar como cliente', import.meta.env.VITE_DEV_TOKEN_CLIENTE], ['Entrar como atendente', import.meta.env.VITE_DEV_TOKEN_ATENDENTE]]
  .filter(([, t]) => t);

export default function Login() {
  const { perfil, carregando } = useAuth();
  const [erro, setErro] = useState(() => {
    try { const a = sessionStorage.getItem('siglog_aviso'); sessionStorage.removeItem('siglog_aviso'); return a || ''; } catch { return ''; }
  });
  const [enviando, setEnviando] = useState(false);
  const [modo, setModo] = useState('entrar'); // 'entrar' | 'criar'
  const [aviso, setAviso] = useState('');
  if (!carregando && perfil) return <Navigate to="/" replace />;

  async function enviar(e) {
    e.preventDefault();
    const f = new FormData(e.target);
    setErro('');
    setAviso('');
    setEnviando(true);
    try {
      if (temSupabase && modo === 'criar') {
        if (f.get('senha').length < 8) throw new Error('A senha precisa ter pelo menos 8 caracteres.');
        if (f.get('senha') !== f.get('confirmar')) throw new Error('As senhas não conferem.');
        const r = await criarConta(f.get('email'), f.get('senha'));
        if (!r.logado) {
          setModo('entrar');
          setAviso('Conta criada! Enviamos um e-mail de confirmação: confirme o endereço e depois entre.');
        }
      } else if (temSupabase) await entrar(f.get('email'), f.get('senha'));
      else entrarComTokenDev(f.get('token'));
    } catch (err) {
      setErro(err.message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <main className="login-pagina">
      <div className="login-fundo"><RouteArt fundo /></div>
      <header className="login-topo marca"><Logo tamanho={34} /> <span>SIG-Log <b>Customer</b></span></header>

      <form className="cartao vidro login-cartao" onSubmit={enviar}>
        <div>
          <h1>{modo === 'criar' ? 'Criar conta' : 'Entrar'}</h1>
          <p className="muted">{modo === 'criar' ? 'Informe um e-mail e uma senha. O e-mail pode ser fictício.' : 'Sua carga, do pedido à entrega.'}</p>
        </div>
        {(temSupabase || temDemo) && (
          <div className="abas abas-login" role="tablist" aria-label="Acesso">
            <button type="button" role="tab" aria-selected={modo === 'entrar'} className={modo === 'entrar' ? 'ativa' : ''} onClick={() => { setModo('entrar'); setErro(''); }}>Entrar</button>
            <button type="button" role="tab" aria-selected={modo === 'criar'} className={modo === 'criar' ? 'ativa' : ''} onClick={() => { setModo('criar'); setErro(''); setAviso(''); }}>Criar conta</button>
          </div>
        )}
        {temDemo ? (
          <p className="alerta info">Modo demonstração: explore o portal com dados fictícios. Nada é enviado a nenhum servidor.</p>
        ) : temSupabase && modo === 'criar' ? (
          <>
            <label className="campo"><span>E-mail</span><input name="email" type="email" autoComplete="email" placeholder="voce@exemplo.com" required autoFocus /></label>
            <label className="campo"><span>Senha</span><input name="senha" type="password" autoComplete="new-password" placeholder="Mínimo de 8 caracteres" minLength={8} required /></label>
            <label className="campo"><span>Confirmar senha</span><input name="confirmar" type="password" autoComplete="new-password" placeholder="Repita a senha" minLength={8} required /></label>
          </>
        ) : temSupabase ? (
          <>
            <label className="campo"><span>E-mail</span><input name="email" type="email" autoComplete="username" placeholder="voce@empresa.com" required autoFocus /></label>
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
        <Alerta tipo="ok">{aviso}</Alerta>
        {temDemo ? (
          <div className="acoes col-demo">
            {modo === 'criar' ? (
              <button type="button" className="primario" onClick={() => entrarDemo('novo')}>Criar conta de demonstração</button>
            ) : (
              <>
                <button type="button" className="primario" onClick={() => entrarDemo('cliente')}>Entrar como cliente (demonstração)</button>
                <button type="button" onClick={() => entrarDemo('atendente')}>Entrar como atendente (demonstração)</button>
              </>
            )}
          </div>
        ) : (
          <button className="primario" disabled={enviando}>{enviando ? (modo === 'criar' ? 'Criando conta…' : 'Entrando…') : (modo === 'criar' ? 'Criar conta' : 'Entrar')}</button>
        )}
        {!temSupabase && !temDemo && RAPIDOS.length > 0 && (
          <div className="acoes">
            {RAPIDOS.map(([rotulo, t]) => <button type="button" key={rotulo} onClick={() => entrarComTokenDev(t)}>{rotulo}</button>)}
          </div>
        )}
      </form>

      <footer className="login-rodape"><SeloEquipe /></footer>
    </main>
  );
}
