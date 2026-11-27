// Sessão e token. Com Supabase configurado, o login é o do Supabase Auth (JWT ES256 validado pela API).
// Sem Supabase (dev local), aceita colar um token gerado por scripts/gen_token.py.
import { createClient } from '@supabase/supabase-js';

const url = import.meta.env.VITE_SUPABASE_URL;
const key = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY;
export const temSupabase = Boolean(url && key);
export const supabase = temSupabase ? createClient(url, key, { auth: { flowType: 'pkce', detectSessionInUrl: true, persistSession: true } }) : null;

// Provedores de login social ligados neste build (VITE_AUTH_PROVIDERS=google,github). Só aparecem os que estiverem aqui.
export const PROVEDORES = (import.meta.env.VITE_AUTH_PROVIDERS || '').split(',').map((p) => p.trim().toLowerCase()).filter((p) => ['google', 'github'].includes(p));

const DEV = 'siglog_dev_token';
const DEMO = 'siglog_demo_papel';
export const temDemo = import.meta.env.VITE_DEMO === 'true';
const guardar = {
  ler: () => { try { return sessionStorage.getItem(DEV); } catch { return null; } },
  gravar: (v) => { try { sessionStorage.setItem(DEV, v); } catch { /* sem storage */ } },
  limpar: () => { try { sessionStorage.removeItem(DEV); } catch { /* sem storage */ } },
};

export async function getToken() {
  if (temDemo) { try { const p = sessionStorage.getItem(DEMO); return p ? `demo:${p}` : null; } catch { return null; } }
  if (supabase) {
    const { data } = await supabase.auth.getSession();
    return data.session?.access_token ?? null;
  }
  return guardar.ler();
}

// Foto, nome e e-mail do login (Supabase). A foto só existe quando a pessoa entra por GitHub/Google.
export async function dadosDoLogin() {
  if (!supabase) return null;
  const { data } = await supabase.auth.getSession();
  const u = data.session?.user;
  if (!u) return null;
  const m = u.user_metadata ?? {};
  return { email: u.email ?? null, nome: m.full_name || m.name || null, avatar: m.avatar_url || m.picture || null };
}

export async function entrar(email, senha) {
  if (!supabase) throw new Error('Supabase não configurado');
  const { error } = await supabase.auth.signInWithPassword({ email, password: senha });
  if (error) {
    throw new Error(error.message === 'Invalid login credentials' ? 'E-mail ou senha incorretos.' : error.message);
  }
}

// Login com Google/GitHub: o Supabase leva ao provedor e volta para esta página já com a sessão aberta.
export async function entrarComProvedor(provedor) {
  if (!supabase) throw new Error('Supabase não configurado');
  const redirectTo = `${window.location.origin}${import.meta.env.BASE_URL}`;
  const { error } = await supabase.auth.signInWithOAuth({ provider: provedor, options: { redirectTo } });
  if (error) throw new Error(/not enabled|unsupported/i.test(error.message || '') ? 'Este tipo de login ainda não foi ativado no sistema.' : (error.message || 'Não foi possível iniciar o login.'));
}

// Cria a conta no Supabase Auth. Conta nova = perfil `cliente` (papel de equipe só pelo servidor, em app_metadata).
// Devolve { logado: true } quando o Supabase já abre a sessão; { logado: false } se o projeto exigir confirmação por e-mail.
export async function criarConta(email, senha) {
  if (!supabase) throw new Error('Supabase não configurado');
  const { data, error } = await supabase.auth.signUp({ email, password: senha });
  if (error) {
    const m = error.message || '';
    if (/already registered|already been registered/i.test(m)) throw new Error('Já existe uma conta com este e-mail. Use a aba "Entrar".');
    if (/password/i.test(m)) throw new Error('Senha fraca ou inválida. Use pelo menos 8 caracteres.');
    if (/rate limit|too many/i.test(m)) throw new Error('Muitas tentativas em pouco tempo. Aguarde alguns minutos e tente de novo.');
    if (/signups? not allowed|disabled/i.test(m)) throw new Error('A criação de contas está desativada neste sistema.');
    throw new Error(m || 'Não foi possível criar a conta.');
  }
  return { logado: Boolean(data.session) };
}

export function entrarComTokenDev(token) {
  guardar.gravar(token.trim());
  window.dispatchEvent(new Event('siglog:sessao'));
}

export function entrarDemo(papel) {
  try { sessionStorage.setItem(DEMO, papel); } catch { /* sem storage */ }
  window.dispatchEvent(new Event('siglog:sessao'));
}

export async function sair() {
  try { sessionStorage.removeItem(DEMO); } catch { /* sem storage */ }
  if (supabase) await supabase.auth.signOut();
  guardar.limpar();
  window.dispatchEvent(new Event('siglog:sessao'));
}
