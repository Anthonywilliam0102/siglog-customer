import { demoApi } from './demo.js';
import { ApiError } from './errors.js';
import { getToken, sair, temDemo } from './session.js';

// Em dev, '/api' é redirecionado pelo Vite para a API local. Em produção use VITE_API_URL.
const BASE = import.meta.env.VITE_API_URL || '/api';

export { ApiError };

function mensagem(data, status) {
  if (typeof data?.detail === 'string') return data.detail;
  if (Array.isArray(data?.detail) && data.detail[0]?.msg) return `Dados inválidos: ${data.detail[0].msg}`;
  return `Erro ${status}`;
}

const esperar = (ms) => new Promise((r) => setTimeout(r, ms));

async function enviar(path, method, body) {
  const token = await getToken();
  return fetch(`${BASE}${path}`, {
    method,
    headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  });
}

export async function api(path, { method = 'GET', body } = {}) {
  if (temDemo) return demoApi(path, { method, body }, await getToken());
  let res = await enviar(path, method, body);
  // Um 401 logo após o login pode ser só defasagem de relógio: tenta de novo antes de encerrar a sessão.
  if (res.status === 401) {
    await esperar(1500);
    res = await enviar(path, method, body);
  }
  const data = await res.json().catch(() => ({}));
  if (res.status === 401) {
    await sair();
    sessionStorage.setItem('siglog_aviso', 'Sua sessão expirou. Entre novamente.');
  }
  if (!res.ok) throw new ApiError(mensagem(data, res.status), res.status);
  return data;
}
