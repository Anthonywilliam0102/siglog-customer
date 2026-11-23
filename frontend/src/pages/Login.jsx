import { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { Alerta } from '../components/ui.jsx';
import { useAuth } from '../auth.jsx';
import { entrar, entrarComTokenDev, temSupabase } from '../session.js';

export default function Login() {
  const { perfil, carregando } = useAuth();
  const [erro, setErro] = useState('');
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
    <main className="login">
      <form className="cartao" onSubmit={enviar}>
        <h1>SIG-Log <b>Customer</b></h1>
        <p className="muted">Portal do cliente: cotação, pedidos, rastreamento e atendimento.</p>
        {temSupabase ? (
          <>
            <label className="campo"><span>E-mail</span><input name="email" type="email" autoComplete="username" required /></label>
            <label className="campo"><span>Senha</span><input name="senha" type="password" autoComplete="current-password" required /></label>
          </>
        ) : (
          <label className="campo">
            <span>Token de desenvolvimento</span>
            <textarea name="token" rows={4} required placeholder="Cole o token gerado por scripts/gen_token.py" />
            <small>Supabase não configurado (VITE_SUPABASE_URL). Modo de desenvolvimento.</small>
          </label>
        )}
        <Alerta>{erro}</Alerta>
        <button className="primario" disabled={enviando}>{enviando ? 'Entrando…' : 'Entrar'}</button>
      </form>
    </main>
  );
}
