// Sessão e token. Com Supabase configurado, o login é o do Supabase Auth (JWT ES256 validado pela API).
// Sem Supabase (dev local), aceita colar um token gerado por scripts/gen_token.py.
import { createClient } from '@supabase/supabase-js';

const url = import.meta.env.VITE_SUPABASE_URL;
const key = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY;
export const temSupabase = Boolean(url && key);
export const supabase = temSupabase ? createClient(url, key) : null;

const DEV = 'siglog_dev_token';
const guardar = {
  ler: () => { try { return sessionStorage.getItem(DEV); } catch { return null; } },
  gravar: (v) => { try { sessionStorage.setItem(DEV, v); } catch { /* sem storage */ } },
  limpar: () => { try { sessionStorage.removeItem(DEV); } catch { /* sem storage */ } },
};

export async function getToken() {
  if (supabase) {
    const { data } = await supabase.auth.getSession();
    return data.session?.access_token ?? null;
  }
  return guardar.ler();
}

export async function entrar(email, senha) {
  if (!supabase) throw new Error('Supabase não configurado');
  const { error } = await supabase.auth.signInWithPassword({ email, password: senha });
  if (error) {
    throw new Error(error.message === 'Invalid login credentials' ? 'E-mail ou senha incorretos.' : error.message);
  }
}

export function entrarComTokenDev(token) {
  guardar.gravar(token.trim());
  window.dispatchEvent(new Event('siglog:sessao'));
}

export async function sair() {
  if (supabase) await supabase.auth.signOut();
  guardar.limpar();
  window.dispatchEvent(new Event('siglog:sessao'));
}
