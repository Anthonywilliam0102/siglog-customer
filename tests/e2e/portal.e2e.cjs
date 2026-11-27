// Teste ponta a ponta do portal, no navegador. NÃO é executado no CI (precisa de API e front no ar).
//
// Modo Supabase (login real pela tela):
//   set -a; . ./.env.validacao; set +a          # CLIENTE_EMAIL, CLIENTE_PW, ATENDENTE_EMAIL, ATENDENTE_PW
//   E2E_MODE=supabase npm test
// Modo desenvolvimento (token HS256 de scripts/gen_token.py; API com JWT_SECRET):
//   E2E_MODE=dev E2E_TOKEN_CLIENTE=... E2E_TOKEN_ATENDENTE=... npm test
// Opcional: E2E_BASE_URL (padrão http://127.0.0.1:5173), E2E_CHANNEL=chrome (usa o Chrome instalado), E2E_SHOTS=pasta.
// Nunca imprime senhas ou tokens. Cria dados de teste (cliente fictício, pedido, chamado, sinistro).
const { chromium } = require('playwright');
const fs = require('fs');

const BASE = process.env.E2E_BASE_URL || 'http://127.0.0.1:5173';
const MODE = process.env.E2E_MODE || 'supabase';
const SHOTS = process.env.E2E_SHOTS || '';
const resultados = [];
const ok = (nome, cond, extra = '') => resultados.push([cond ? 'OK   ' : 'FALHA', nome, cond ? '' : extra]);

function cnpjValido() {
  const d = Array.from({ length: 8 }, () => Math.floor(Math.random() * 10)).concat([0, 0, 0, 1]);
  const dv = (n, p) => { const r = d.slice(0, n).reduce((a, x, i) => a + x * p[i], 0) % 11; return r < 2 ? 0 : 11 - r; };
  d.push(dv(12, [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]));
  d.push(dv(13, [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]));
  return d.join('');
}
const exigir = (nome) => { if (!process.env[nome]) { console.error(`Variável ${nome} ausente.`); process.exit(2); } return process.env[nome]; };
const shot = async (page, nome) => { if (SHOTS) { fs.mkdirSync(SHOTS, { recursive: true }); await page.screenshot({ path: `${SHOTS}/${nome}.png` }); } };

async function entrar(page, quem) {
  await page.goto(`${BASE}/login`);
  if (MODE === 'dev') {
    await page.fill('textarea[name=token]', exigir(`E2E_TOKEN_${quem.toUpperCase()}`));
  } else {
    await page.fill('input[name=email]', exigir(`${quem.toUpperCase()}_EMAIL`));
    await page.fill('input[name=senha]', exigir(`${quem.toUpperCase()}_PW`));
  }
  await page.click('button.primario');
  await page.waitForFunction(() => !location.pathname.startsWith('/login'), null, { timeout: 15000 });
  await page.waitForLoadState('networkidle');
}
const sair = async (page) => { await page.click('button.link'); await page.waitForURL('**/login'); };

(async () => {
  const browser = await chromium.launch(process.env.E2E_CHANNEL ? { channel: process.env.E2E_CHANNEL } : {});
  const page = await (await browser.newContext({ viewport: { width: 1280, height: 800 } })).newPage();
  const erros = [];
  page.on('pageerror', (e) => erros.push(`pageerror: ${e.message}`));
  page.on('response', (r) => { if (r.url().includes('/api/') && r.status() >= 500) erros.push(`HTTP ${r.status()} ${r.url()}`); });

  await page.goto(`${BASE}/pedidos`);
  await page.waitForURL('**/login', { timeout: 5000 }).catch(() => {});
  ok('sem sessão vai para /login', page.url().endsWith('/login'), page.url());

  // ---- cliente ----
  await entrar(page, 'cliente');
  if (page.url().endsWith('/cadastro')) {
    await page.check('input[type=radio] >> nth=1');
    await page.fill('input[name=nome]', 'Loja Teste E2E Ltda');
    await page.fill('input[name=documento]', cnpjValido());
    await page.fill('input[name=email]', 'e2e@example.com');
    await page.click('button.primario');
    await page.waitForURL(`${BASE}/`);
    ok('cadastro do cliente novo', true);
  }
  ok('cliente chega ao início', page.url() === `${BASE}/`, page.url());
  await shot(page, '01_home_cliente');

  await page.click('text=Nova cotação >> nth=0');
  await page.fill('input[name=origem]', 'São Paulo/SP');
  await page.fill('input[name=destino]', 'Recife/PE');
  await page.fill('input[name=peso]', '120.5');
  await page.fill('input[name=volume]', '1.2');
  await page.click('button.primario');
  await page.waitForSelector('.valor');
  ok('cotação mostra o valor (R$ 290,40)', (await page.textContent('.valor')).includes('290,40'), await page.textContent('.valor'));
  await shot(page, '02_cotacao');
  await page.click('text=Confirmar pedido');
  await page.waitForURL(/\/pedidos\/[0-9a-f-]+$/);
  const pedidoUrl = page.url();
  await page.waitForSelector('text=Rastreamento');
  ok('pedido criado e detalhe aberto', (await page.textContent('h1')).startsWith('Pedido #'));
  await shot(page, '03_pedido');

  await page.click('text=Abrir chamado');
  await page.fill('input[name=assunto]', 'Previsão de entrega (E2E)');
  await page.fill('textarea[name=mensagem]', 'Qual a previsão de entrega?');
  await page.selectOption('select[name=prioridade]', 'ALTA');
  await page.click('button.primario');
  await page.waitForURL(/\/chamados\/[0-9a-f-]+$/);
  const chamadoUrl = page.url();
  await page.waitForSelector('text=Vence em', { timeout: 8000 }).catch(() => {});
  ok('chamado criado com SLA visível', (await page.textContent('body')).includes('Vence em'));

  await page.goto(pedidoUrl);
  await page.click('text=Registrar sinistro');
  await page.selectOption('select[name=tipo]', 'AVARIA');
  await page.fill('input[name=valor]', '150.00');
  await page.fill('textarea[name=descricao]', 'Caixa amassada (E2E)');
  await page.click('button.primario');
  await page.waitForURL(`${BASE}/sinistros`);
  ok('sinistro listado', (await page.textContent('table')).includes('AVARIA'));

  await page.goto(`${BASE}/atendimento`);
  await page.waitForURL(`${BASE}/`, { timeout: 5000 }).catch(() => {});
  ok('cliente não acessa /atendimento (RN02 na tela)', page.url() === `${BASE}/`, page.url());
  await sair(page);

  // ---- atendente ----
  await entrar(page, 'atendente');
  ok('atendente entra sem cadastro', page.url() === `${BASE}/`, page.url());
  await page.goto(`${BASE}/atendimento`);
  await page.waitForSelector('table');
  ok('fila mostra o chamado do cliente', (await page.textContent('table')).includes('Previsão de entrega (E2E)'));
  await shot(page, '04_fila');
  await page.goto(chamadoUrl);
  await page.fill('textarea[name=mensagem]', 'Previsão: 3 dias úteis.');
  await page.click('text=Enviar resposta');
  await page.waitForSelector('.mensagem.equipe');
  ok('resposta da equipe na conversa', (await page.textContent('.conversa')).includes('3 dias úteis'));
  await page.click('text=Marcar como resolvido');
  await page.waitForSelector('.alerta.ok');
  ok('chamado resolvido', true);

  await page.goto(pedidoUrl);
  for (const rot of ['em separação', 'em transporte', 'entregue']) {
    await page.click(`button:has-text("Marcar como ${rot}")`);
    await page.waitForTimeout(700);
  }
  ok('pedido chegou a Entregue (RN07)', (await page.textContent('.cabecalho')).includes('Entregue'));
  ok('rastreamento com 4 eventos', (await page.locator('.eventos li').count()) === 4);
  await shot(page, '05_pedido_entregue');
  await sair(page);

  // ---- cliente avalia ----
  await entrar(page, 'cliente');
  await page.goto(pedidoUrl);
  await page.click('.estrelas button >> nth=4');
  await page.click('text=Enviar avaliação');
  await page.waitForSelector('.alerta.ok');
  ok('avaliação da entrega', true);
  await page.goto(chamadoUrl);
  await page.click('.estrelas button >> nth=3');
  await page.click('text=Enviar avaliação');
  await page.waitForSelector('text=Obrigado pela avaliação');
  ok('avaliação do atendimento', true);

  ok('sem erros de página nem HTTP 5xx', erros.length === 0, erros.join(' | '));
  await browser.close();
  for (const [s, n, e] of resultados) console.log(s, n, e ? `(${e})` : '');
  const falhas = resultados.filter((r) => r[0] === 'FALHA').length;
  console.log(`\n${resultados.length - falhas}/${resultados.length} verificações OK`);
  process.exit(falhas ? 1 : 0);
})().catch((e) => { console.error('ERRO NO TESTE:', e.message); process.exit(1); });
