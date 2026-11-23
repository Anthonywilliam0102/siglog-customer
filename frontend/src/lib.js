// Utilidades de formatação e regras de apresentação (sem dependências de React).
export const brl = (v) => Number(v).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
export const dataHora = (iso) => (iso ? new Date(iso).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' }) : '—');
export const curto = (id) => String(id).slice(0, 8).toUpperCase();

export const STATUS_PEDIDO = {
  CRIADO: { label: 'Criado', tom: 'info' },
  EM_SEPARACAO: { label: 'Em separação', tom: 'info' },
  EM_TRANSPORTE: { label: 'Em transporte', tom: 'aviso' },
  ENTREGUE: { label: 'Entregue', tom: 'ok' },
  CANCELADO: { label: 'Cancelado', tom: 'erro' },
};
export const ETAPAS = ['CRIADO', 'EM_SEPARACAO', 'EM_TRANSPORTE', 'ENTREGUE'];
// Mesmas transições do backend (RN07).
export const PROXIMOS = {
  CRIADO: ['EM_SEPARACAO', 'CANCELADO'],
  EM_SEPARACAO: ['EM_TRANSPORTE', 'CANCELADO'],
  EM_TRANSPORTE: ['ENTREGUE'],
  ENTREGUE: [],
  CANCELADO: [],
};
export const STATUS_TICKET = {
  ABERTO: { label: 'Aberto', tom: 'info' },
  EM_ATENDIMENTO: { label: 'Em atendimento', tom: 'aviso' },
  RESOLVIDO: { label: 'Resolvido', tom: 'ok' },
};
export const PRIORIDADES = { ALTA: 'Alta (4 h)', MEDIA: 'Média (24 h)', BAIXA: 'Baixa (72 h)' };
export const CATEGORIAS = ['ATRASO', 'DUVIDA', 'COBRANCA', 'ENTREGA', 'OUTRO'];
export const TIPOS_SINISTRO = ['AVARIA', 'EXTRAVIO', 'ROUBO', 'OUTRO'];

// SLA: texto e tom conforme o prazo.
export function sla(ticket, agora = Date.now()) {
  if (ticket.status === 'RESOLVIDO') return { texto: 'Concluído', tom: 'ok' };
  const resta = new Date(ticket.sla_due_at).getTime() - agora;
  const h = Math.abs(resta) / 36e5;
  const fmt = h >= 24 ? `${Math.floor(h / 24)} d` : h >= 1 ? `${Math.floor(h)} h` : `${Math.max(1, Math.round(h * 60))} min`;
  return resta < 0 ? { texto: `Vencido há ${fmt}`, tom: 'erro' } : { texto: `Vence em ${fmt}`, tom: resta < 36e5 * 2 ? 'aviso' : 'info' };
}

// Validação de CPF/CNPJ (espelha o backend) para avisar antes de enviar.
const so = (s) => s.replace(/\D/g, '');
export function documentoValido(doc, tipo) {
  const d = so(doc);
  if (tipo === 'PF') {
    if (d.length !== 11 || /^(\d)\1+$/.test(d)) return false;
    for (const n of [9, 10]) {
      let s = 0;
      for (let i = 0; i < n; i++) s += Number(d[i]) * (n + 1 - i);
      if (Number(d[n]) !== ((s * 10) % 11) % 10) return false;
    }
    return true;
  }
  if (d.length !== 14 || /^(\d)\1+$/.test(d)) return false;
  const pesos = [[5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2], [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]];
  return [12, 13].every((n, k) => {
    const s = pesos[k].reduce((a, p, i) => a + Number(d[i]) * p, 0);
    return Number(d[n]) === (s % 11 < 2 ? 0 : 11 - (s % 11));
  });
}
export const soDigitos = so;
