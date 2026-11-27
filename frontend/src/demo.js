// MODO DEMONSTRAÇÃO: simula a API dentro do navegador (dados fictícios, sem servidor).
// Ativado só em build com VITE_DEMO=true. Replica as regras do backend (RN02, RN07, SLA, cotação) para a interface se comportar igual.
import { ApiError } from './errors.js';

const CHAVE = 'siglog_demo_estado';
const H = 36e5;
const SLA_H = { ALTA: 4, MEDIA: 24, BAIXA: 72 };
const PROXIMOS = { CRIADO: ['EM_SEPARACAO', 'CANCELADO'], EM_SEPARACAO: ['EM_TRANSPORTE', 'CANCELADO'], EM_TRANSPORTE: ['ENTREGUE'], ENTREGUE: [], CANCELADO: [] };
const PASSOS = [['Coletado', 'Coletado no centro de distribuição de {o}'], ['Em trânsito', 'Em trânsito entre {o} e {d}'],
  ['Saiu para entrega', 'Saiu para entrega em {d}'], ['Entregue', 'Entregue ao destinatário em {d}']];
const FEITOS = { CRIADO: 0, EM_SEPARACAO: 0, EM_TRANSPORTE: 2, ENTREGUE: 4, CANCELADO: 0 };
const ESPERA = { CRIADO: 'Aguardando separação', EM_SEPARACAO: 'Em separação no CD', CANCELADO: 'Pedido cancelado' };

const uid = () => crypto.randomUUID();
const iso = (t) => new Date(t).toISOString();
const valor = (kg, m3) => (50 + kg * 0.8 + m3 * 120).toFixed(2);

function semente() {
  const agora = Date.now();
  const cid = uid();
  const clientes = [{ id: cid, owner_sub: 'demo-cliente', nome: 'Loja Horizonte Ltda', documento: '11222333000181', tipo: 'PJ', email: 'contato@horizonte.example', telefone: null, endereco: null, created_at: iso(agora - 30 * 24 * H) }];
  const rotas = [['São Paulo/SP', 'Recife/PE', 120.5, 1.2, 'CRIADO'], ['Curitiba/PR', 'Porto Alegre/RS', 40, 0.4, 'EM_SEPARACAO'],
    ['Belo Horizonte/MG', 'Salvador/BA', 310, 2.8, 'EM_TRANSPORTE'], ['Rio de Janeiro/RJ', 'Brasília/DF', 75, 0.9, 'ENTREGUE'], ['Manaus/AM', 'Belém/PA', 220, 2.1, 'ENTREGUE']];
  const pedidos = rotas.map(([origem, destino, kg, m3, status], i) => ({ id: uid(), customer_id: cid, quote_id: uid(), status, origem, destino,
    valor_estimado: valor(kg, m3), created_at: iso(agora - (i + 1) * 5 * H) }));
  const t = (assunto, categoria, prioridade, status, pedido, horas, mensagens) => ({ id: uid(), customer_id: cid, order_id: pedido.id, categoria, prioridade, assunto, status,
    sla_due_at: iso(agora - horas * H + SLA_H[prioridade] * H), created_at: iso(agora - horas * H), mensagens });
  const m = (papel, texto, ago) => ({ id: uid(), author_role: papel, mensagem: texto, created_at: iso(agora - ago * H) });
  const tickets = [
    t('Atraso na coleta', 'ATRASO', 'ALTA', 'ABERTO', pedidos[1], 6, [m('cliente', 'A coleta prevista para hoje não aconteceu. Podem verificar?', 6)]),
    t('Dúvida sobre cobrança', 'COBRANCA', 'MEDIA', 'EM_ATENDIMENTO', pedidos[2], 3, [m('cliente', 'Qual a data de vencimento da cobrança deste pedido?', 3), m('atendente', 'Olá! Estamos verificando com o financeiro e retornamos ainda hoje.', 2)]),
    t('Alteração de endereço', 'OUTRO', 'BAIXA', 'RESOLVIDO', pedidos[0], 20, [m('cliente', 'Preciso alterar o endereço de entrega.', 20), m('atendente', 'Endereço atualizado conforme solicitado.', 19)]),
  ];
  const sinistros = [{ id: uid(), order_id: pedidos[3].id, customer_id: cid, tipo: 'AVARIA', descricao: 'Duas caixas chegaram amassadas.', valor_reclamado: '180.00', status: 'REGISTRADO', created_at: iso(agora - 2 * H) }];
  return { clientes, cotacoes: [], pedidos, tickets, sinistros, avaliacoes: [{ target: 'ENTREGA', order_id: pedidos[3].id }], integracoes: {} };
}

function carregar() {
  try { const s = sessionStorage.getItem(CHAVE); if (s) return JSON.parse(s); } catch { /* sem storage */ }
  const novo = semente();
  salvar(novo);
  return novo;
}
function salvar(e) { try { sessionStorage.setItem(CHAVE, JSON.stringify(e)); } catch { /* sem storage */ } }

const SEM_ATENDENTE = 'Apenas a equipe pode alterar o status';
const out = (o) => { const { owner_sub, ...resto } = o; return resto; }; // eslint-disable-line no-unused-vars

export async function demoApi(caminho, { method = 'GET', body } = {}, token) {
  await new Promise((r) => setTimeout(r, 120)); // sensação de rede
  const quem = (token || '').split(':')[1]; // 'cliente' | 'atendente' | 'novo' (conta criada na demonstração)
  if (!quem) throw new ApiError('Token ausente', 401);
  const papel = quem === 'novo' ? 'cliente' : quem;
  const sub = `demo-${quem}`;
  const equipe = papel === 'atendente';
  const e = carregar();
  const [rota, qs = ''] = caminho.split('?');
  const q = new URLSearchParams(qs);
  const seg = rota.split('/').filter(Boolean);
  const limite = Number(q.get('limit') || 50);
  const meu = (clienteId) => equipe || e.clientes.find((c) => c.id === clienteId)?.owner_sub === sub;
  const nega = () => { throw new ApiError('Acesso negado', 403); };
  const nao = (x) => { throw new ApiError(`${x} não encontrado(a)`, 404); };
  const ordenar = (l) => [...l].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

  if (seg[0] === 'me') return { sub, role: papel };

  const NOMES = { wms: 'Squad 01 · WMS & Estoque', frota: 'Squad 02 · Frota & Roteirização', tracking: 'Squad 03 · Rastreamento', financeiro: 'Squad 04 · Financeiro', rh: 'Squad 05 · RH & Jornada' };
  const FUNCAO = {
    wms: 'Mostra no pedido o andamento da separação no centro de distribuição.',
    frota: 'Reservado: contrato ainda não definido com o Squad 02 (pode consumir o evento EntregaAvaliada).',
    tracking: 'Mostra o rastreamento do pedido (posição e eventos de entrega).',
    financeiro: 'Mostra no pedido a cobrança e o frete.',
    rh: 'Reservado: contrato ainda não definido com o Squad 05.',
  };

  if (seg[0] === 'settings' && seg[1] === 'api-keys') {
    if (!equipe) throw new ApiError('Apenas a equipe pode ver ou alterar as integrações', 403);
    const ks = (e.chaves ??= []);
    if (method === 'GET') return ks;
    if (method === 'POST') {
      if (!NOMES[body.squad]) nao('Squad');
      const chave = `sk_${uid().replace(/-/g, '')}${uid().replace(/-/g, '').slice(0, 11)}`;
      const k = { id: uid(), squad: body.squad, nome: body.nome, prefixo: chave.slice(0, 8), created_at: iso(Date.now()), revoked_at: null, last_used_at: null };
      ks.unshift(k); salvar(e); return { ...k, chave };
    }
    const k = ks.find((x) => x.id === seg[2]); if (!k) nao('Chave'); k.revoked_at = iso(Date.now()); salvar(e); return k;
  }

  if (seg[0] === 'integrations' && seg[1] === 'status') {
    return Object.keys(NOMES).map((sq) => ({ squad: sq, nome: NOMES[sq], funcao: FUNCAO[sq],
      modo: (e.integracoes ?? {})[sq]?.base_url ? 'configurada' : ['frota', 'rh'].includes(sq) ? 'nao_configurada' : 'simulada' }));
  }

  if (seg[0] === 'orders' && seg[2] === 'squads') {
    const o = e.pedidos.find((x) => x.id === seg[1]); if (!o) nao('Pedido'); if (!meu(o.customer_id)) nega();
    const wms = { CRIADO: ['Aguardando separação', 0], EM_SEPARACAO: ['Em separação', 3], EM_TRANSPORTE: ['Enviado ao transporte', 5], ENTREGUE: ['Enviado ao transporte', 5], CANCELADO: ['Cancelado', 0] }[o.status];
    const fin = { ENTREGUE: 'Paga', CANCELADO: 'Estornada' }[o.status] ?? 'Cobrança pendente';
    const venc = new Date(new Date(o.created_at).getTime() + 7 * 24 * H).toLocaleDateString('pt-BR');
    return [
      { squad: 'wms', titulo: 'Separação no CD (WMS)', fonte: 'simulado', status: wms[0], mensagem: null,
        detalhes: [{ rotulo: 'Itens separados', valor: `${wms[1]} de 5` }] },
      { squad: 'financeiro', titulo: 'Cobrança e frete (Financeiro)', fonte: 'simulado', status: fin, mensagem: null,
        detalhes: [{ rotulo: 'Valor', valor: `R$ ${Number(o.valor_estimado).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}` }, { rotulo: 'Vencimento', valor: venc }] },
    ];
  }

  if (seg[0] === 'settings' && seg[1] === 'integrations') {
    if (!equipe) throw new ApiError('Apenas a equipe pode ver ou alterar as integrações', 403);
    const vista = (sq) => { const c = (e.integracoes ??= {})[sq] ?? {}; return { squad: sq, nome: NOMES[sq], base_url: c.base_url ?? null, header_name: c.header_name ?? 'X-API-Key', tem_chave: !!c.tem_chave, atualizado_em: c.atualizado_em ?? null, atualizado_por: c.atualizado_por ?? null }; };
    if (seg.length === 2) return Object.keys(NOMES).map(vista);
    const sq = seg[2]; if (!NOMES[sq]) nao('Squad');
    if (seg[3] === 'test') {
      if (!(e.integracoes ?? {})[sq]?.base_url) throw new ApiError('Configure a URL antes de testar a conexão', 422);
      return { ok: false, status_http: null, ms: 0, erro: 'No modo demonstração não há conexão real com o outro squad.' };
    }
    const c = ((e.integracoes ??= {})[sq] ??= {});
    if (typeof body.base_url === 'string') {
      const u = body.base_url.trim().replace(/\/$/, '');
      if (u && !/^https:\/\/[^/\s]+/.test(u)) throw new ApiError('Use uma URL completa começando com https://', 422);
      c.base_url = u || null;
    }
    if (body.header_name) c.header_name = body.header_name;
    if (body.limpar_chave) c.tem_chave = false;
    if (body.api_key) c.tem_chave = true; // a demonstração nem guarda o valor
    c.atualizado_em = iso(Date.now()); c.atualizado_por = sub;
    salvar(e); return vista(sq);
  }

  if (seg[0] === 'customers') {
    if (seg.length === 1 && method === 'GET') return e.clientes.filter((c) => equipe || c.owner_sub === sub).slice(0, limite).map(out);
    if (seg.length === 1 && method === 'POST') {
      if (e.clientes.some((c) => c.documento === body.documento)) throw new ApiError('Já existe cliente com este documento', 409);
      const c = { id: uid(), owner_sub: sub, ...body, created_at: iso(Date.now()) };
      e.clientes.push(c); salvar(e); return out(c);
    }
    const c = e.clientes.find((x) => x.id === seg[1]); if (!c) nao('Cliente'); if (!meu(c.id)) nega(); return out(c);
  }

  if (seg[0] === 'quotes' && method === 'POST') {
    if (!meu(body.customer_id)) nega();
    const c = { id: uid(), customer_id: body.customer_id, origem: body.origem, destino: body.destino, peso_kg: body.peso_kg, volume_m3: body.volume_m3,
      valor_estimado: valor(body.peso_kg, body.volume_m3), expires_at: iso(Date.now() + 24 * H), accepted: false, created_at: iso(Date.now()) };
    e.cotacoes.push(c); salvar(e); return c;
  }

  if (seg[0] === 'orders') {
    if (seg.length === 1 && method === 'GET') {
      let l = e.pedidos.filter((p) => meu(p.customer_id));
      if (q.get('status')) l = l.filter((p) => p.status === q.get('status'));
      if (q.get('customer_id')) l = l.filter((p) => p.customer_id === q.get('customer_id'));
      return ordenar(l).slice(0, limite);
    }
    if (seg.length === 1 && method === 'POST') {
      const c = e.cotacoes.find((x) => x.id === body.quote_id); if (!c) nao('Cotação'); if (!meu(c.customer_id)) nega();
      if (c.accepted) throw new ApiError('Cotação já utilizada em um pedido', 409);
      if (new Date(c.expires_at) <= Date.now()) throw new ApiError('Cotação expirada', 422);
      c.accepted = true;
      const p = { id: uid(), customer_id: c.customer_id, quote_id: c.id, status: 'CRIADO', origem: c.origem, destino: c.destino, valor_estimado: c.valor_estimado, created_at: iso(Date.now()) };
      e.pedidos.push(p); salvar(e); return p;
    }
    const p = e.pedidos.find((x) => x.id === seg[1]); if (!p) nao('Pedido'); if (!meu(p.customer_id)) nega();
    if (seg[2] === 'tracking') {
      const feitos = FEITOS[p.status];
      const base = new Date(p.created_at).getTime();
      const events = PASSOS.slice(0, feitos).map(([, t], i) => ({ timestamp: iso(base + 6 * H * (i + 1)), description: t.replace('{o}', p.origem).replace('{d}', p.destino), location: i < 2 ? p.origem : p.destino }));
      return { order_id: p.id, status: feitos ? PASSOS[feitos - 1][0] : ESPERA[p.status], events, source: 'mock' };
    }
    if (seg[2] === 'status' && method === 'PATCH') {
      if (!equipe) throw new ApiError(SEM_ATENDENTE, 403);
      if (body.status === p.status) return p;
      if (!PROXIMOS[p.status].includes(body.status)) throw new ApiError(`Transição de status inválida: ${p.status} -> ${body.status}`, 422);
      p.status = body.status; salvar(e); return p;
    }
    return p;
  }

  if (seg[0] === 'tickets') {
    const detalhe = (t) => ({ ...t, messages: t.mensagens });
    const semMsgs = (t) => { const { mensagens, ...r } = t; return r; }; // eslint-disable-line no-unused-vars
    if (seg.length === 1 && method === 'GET') {
      let l = e.tickets.filter((t) => meu(t.customer_id));
      if (q.get('status')) l = l.filter((t) => t.status === q.get('status'));
      return ordenar(l).slice(0, limite).map(semMsgs);
    }
    if (seg.length === 1 && method === 'POST') {
      if (!meu(body.customer_id)) nega();
      const t = { id: uid(), customer_id: body.customer_id, order_id: body.order_id, categoria: body.categoria, prioridade: body.prioridade, assunto: body.assunto, status: 'ABERTO',
        sla_due_at: iso(Date.now() + SLA_H[body.prioridade] * H), created_at: iso(Date.now()),
        mensagens: [{ id: uid(), author_role: papel, mensagem: body.mensagem, created_at: iso(Date.now()) },
          { id: uid(), author_role: 'sistema', created_at: iso(Date.now() + 5),
            mensagem: `Recebemos o seu chamado. Prioridade ${body.prioridade.toLowerCase()}: nossa equipe responde em até ${SLA_H[body.prioridade]} h. Aguarde, vamos falar com você por aqui. Pode enviar novas informações a qualquer momento.` }] };
      e.tickets.push(t); salvar(e); return semMsgs(t);
    }
    const t = e.tickets.find((x) => x.id === seg[1]); if (!t) nao('Ticket'); if (!meu(t.customer_id)) nega();
    if (seg[2] === 'messages' && method === 'POST') {
      if (t.status === 'RESOLVIDO') throw new ApiError('Ticket resolvido não aceita novas mensagens', 422);
      t.mensagens.push({ id: uid(), author_role: papel, mensagem: body.mensagem, created_at: iso(Date.now()) });
      if (equipe && t.status === 'ABERTO') t.status = 'EM_ATENDIMENTO';
      salvar(e); return semMsgs(t);
    }
    if (seg[2] === 'status' && method === 'PATCH') {
      if (!equipe) throw new ApiError(SEM_ATENDENTE, 403);
      t.status = body.status; salvar(e); return semMsgs(t);
    }
    return detalhe(t);
  }

  if (seg[0] === 'claims') {
    if (method === 'GET') return ordenar(e.sinistros.filter((s) => meu(s.customer_id))).slice(0, limite);
    const p = e.pedidos.find((x) => x.id === body.order_id); if (!p) nao('Pedido'); if (!meu(p.customer_id)) nega();
    if (p.status === 'CANCELADO') throw new ApiError('Pedido cancelado não aceita sinistro', 422);
    const s = { id: uid(), order_id: p.id, customer_id: p.customer_id, tipo: body.tipo, descricao: body.descricao, valor_reclamado: String(body.valor_reclamado), status: 'REGISTRADO', created_at: iso(Date.now()) };
    e.sinistros.push(s); salvar(e); return s;
  }

  if (seg[0] === 'feedback' && method === 'POST') {
    const chaveId = body.target === 'ENTREGA' ? body.order_id : body.ticket_id;
    if (!chaveId) throw new ApiError(body.target === 'ENTREGA' ? 'order_id é obrigatório para avaliar a entrega' : 'ticket_id é obrigatório para avaliar o atendimento', 422);
    if (body.target === 'ENTREGA') {
      const p = e.pedidos.find((x) => x.id === body.order_id); if (!p) nao('Pedido'); if (!meu(p.customer_id)) nega();
      if (p.status !== 'ENTREGUE') throw new ApiError('A entrega só pode ser avaliada após o pedido ser entregue', 422);
    }
    if (e.avaliacoes.some((a) => a.target === body.target && (a.order_id ?? a.ticket_id) === chaveId)) throw new ApiError('Este item já foi avaliado', 409);
    e.avaliacoes.push({ target: body.target, order_id: body.order_id, ticket_id: body.ticket_id }); salvar(e);
    return { id: uid(), target: body.target, nota: body.nota, comentario: body.comentario ?? null, order_id: body.order_id ?? null, ticket_id: body.ticket_id ?? null };
  }

  throw new ApiError(`Rota não disponível na demonstração: ${method} ${rota}`, 404);
}
