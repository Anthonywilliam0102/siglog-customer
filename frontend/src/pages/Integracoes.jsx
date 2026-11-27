import { useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api.js';
import { Alerta, Cabecalho, Campo, Carregando, Selo } from '../components/ui.jsx';
import Icon from '../components/Icons.jsx';
import Voltar from '../components/Voltar.jsx';
import { useToast } from '../components/Toast.jsx';
import { useAuth } from '../auth.jsx';
import { useCarga } from '../hooks.js';
import { dataHora } from '../lib.js';

const MODOS = {
  configurada: ['ok', 'Conectada'],
  simulada: ['info', 'Simulada (demonstração)'],
  nao_configurada: ['info', 'Não configurada'],
};

function Formulario({ item, aoSalvar }) {
  const toast = useToast();
  const [chave, setChave] = useState('');
  const [erro, setErro] = useState('');
  const [ocupado, setOcupado] = useState(false);
  const [teste, setTeste] = useState(null);

  async function enviar(e, limparChave = false) {
    e.preventDefault();
    const f = new FormData(e.target.form ?? e.target);
    setErro('');
    setOcupado(true);
    try {
      const corpo = { base_url: f.get('base_url') ?? '', header_name: f.get('header_name') || 'X-API-Key', limpar_chave: limparChave };
      if (chave) corpo.api_key = chave;
      await api(`/settings/integrations/${item.squad}`, { method: 'PUT', body: corpo });
      setChave('');
      setTeste(null);
      toast.ok(limparChave ? 'Chave removida.' : `Integração com ${item.nome.split(' · ')[1]} salva.`);
      aoSalvar();
    } catch (err) {
      setErro(err.message);
    } finally {
      setOcupado(false);
    }
  }

  async function testar() {
    setTeste({ carregando: true });
    try {
      setTeste(await api(`/settings/integrations/${item.squad}/test`, { method: 'POST' }));
    } catch (err) {
      setTeste({ ok: false, erro: err.message });
    }
  }

  return (
    <form className="integracao-form" onSubmit={enviar}>
      <Campo label="URL base da API"><input name="base_url" defaultValue={item.base_url ?? ''} placeholder="https://api.squad.exemplo.com" inputMode="url" /></Campo>
      <div className="duas">
        <Campo label="Cabeçalho da chave"><input name="header_name" defaultValue={item.header_name} placeholder="X-API-Key" /></Campo>
        <Campo label="Chave de API" ajuda={item.tem_chave ? 'Já existe uma chave guardada; digite para trocar.' : 'Guardada cifrada no servidor.'}>
          <input type="password" autoComplete="new-password" value={chave} onChange={(e) => setChave(e.target.value)} placeholder={item.tem_chave ? '••••••••••••' : 'cole a chave aqui'} />
        </Campo>
      </div>
      <Alerta>{erro}</Alerta>
      <div className="acoes esq">
        <button className="primario" disabled={ocupado}>{ocupado ? 'Salvando…' : 'Salvar'}</button>
        <button type="button" disabled={ocupado || !item.base_url} onClick={testar}><Icon nome="refresh" tamanho={16} /> Testar conexão</button>
        {item.tem_chave && <button type="button" className="perigo" disabled={ocupado} onClick={(e) => enviar(e, true)}>Remover chave</button>}
        {item.atualizado_em && <span className="muted pequeno">Atualizado em {dataHora(item.atualizado_em)}</span>}
      </div>
      {teste?.carregando && <Carregando texto="Testando…" />}
      {teste && !teste.carregando && (teste.ok
        ? <Alerta tipo="ok">Respondeu {teste.status_http} em {teste.ms} ms.</Alerta>
        : <Alerta>{teste.erro ?? `O serviço respondeu com erro (${teste.status_http}).`}</Alerta>)}
    </form>
  );
}

const ONDE = {
  wms: 'Detalhe do pedido → "Separação no CD (WMS)": itens separados e situação da separação.',
  tracking: 'Detalhe do pedido → "Rastreamento": situação e eventos de entrega.',
  financeiro: 'Detalhe do pedido → "Cobrança e frete (Financeiro)": situação, valor e vencimento.',
  frota: 'Ainda sem tela: aguardando o contrato do squad.',
  rh: 'Ainda sem tela: aguardando o contrato do squad.',
};

function Aba({ status, config, equipe, aoSalvar }) {
  const [tom, rotulo] = MODOS[status.modo] ?? MODOS.nao_configurada;
  return (
    <article className="cartao integracao" data-squad={status.squad}>
      <div className="integracao-topo">
        <h3>{status.nome}</h3>
        <Selo tom={tom}>{rotulo}</Selo>
      </div>
      <p>{status.funcao}</p>
      <p className="linha-info"><span>Onde aparece no portal</span>{ONDE[status.squad]}</p>
      {status.modo === 'simulada' && <p className="pequeno muted">Enquanto o squad não conecta a API real, o portal mostra dados simulados, sempre identificados como tal.</p>}
      {!equipe && <p className="pequeno muted">A configuração da conexão é feita pela equipe de atendimento.</p>}
      {equipe && config && <Formulario key={`${config.squad}-${config.atualizado_em}`} item={config} aoSalvar={aoSalvar} />}
    </article>
  );
}

function NossaApi() {
  const toast = useToast();
  const { dados, erro, carregando, recarregar } = useCarga(() => api('/settings/api-keys'), []);
  const [nova, setNova] = useState(null);
  const [msg, setMsg] = useState('');
  const base = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '');

  async function emitir(e) {
    e.preventDefault();
    const f = new FormData(e.target);
    setMsg('');
    try {
      setNova(await api('/settings/api-keys', { method: 'POST', body: { squad: f.get('squad'), nome: f.get('nome') } }));
      e.target.reset();
      recarregar();
    } catch (err) { setMsg(err.message); }
  }
  async function revogar(k) {
    try { await api(`/settings/api-keys/${k.id}`, { method: 'DELETE' }); toast.ok('Chave revogada.'); recarregar(); } catch (err) { setMsg(err.message); }
  }
  async function copiar(t) {
    try { await navigator.clipboard.writeText(t); toast.ok('Copiado.'); } catch { toast.erro('Não foi possível copiar; selecione e copie manualmente.'); }
  }

  return (
    <article className="cartao integracao" data-squad="nossa-api">
      <div className="integracao-topo"><h3>Nossa API · para os outros squads</h3><Selo tom="ok">Somente leitura</Selo></div>
      <p>Gere uma chave para cada squad que precisa consultar os pedidos do CRM. Com ela, o outro squad chama <code>GET /orders</code> e <code>GET /orders/{'{id}'}</code> enviando o cabeçalho <code>X-API-Key</code>. A chave <b>não consegue alterar nada</b>.</p>
      <p className="linha-info"><span>Endereço da API</span><code>{base.startsWith('http') ? base : 'a URL pública da API (ver Configurações)'}</code></p>
      <p className="linha-info"><span>Documentação</span>{base.startsWith('http') ? <code>{base}/docs</code> : <code>/docs</code>}</p>
      <form className="integracao-form" onSubmit={emitir}>
        <div className="duas">
          <Campo label="Squad que vai usar"><select name="squad" defaultValue="wms"><option value="wms">Squad 01 · WMS</option><option value="frota">Squad 02 · Frota</option><option value="tracking">Squad 03 · Rastreamento</option><option value="financeiro">Squad 04 · Financeiro</option><option value="rh">Squad 05 · RH</option></select></Campo>
          <Campo label="Descrição da chave"><input name="nome" required minLength={3} maxLength={80} placeholder="Integração do WMS (produção)" /></Campo>
        </div>
        <Alerta>{msg || erro}</Alerta>
        <div className="acoes esq"><button className="primario">Gerar chave</button></div>
      </form>
      {nova && (
        <Alerta tipo="ok">
          <b>Copie agora: esta chave aparece uma única vez.</b>
          <p className="linha-info"><code className="chave-nova">{nova.chave}</code> <button type="button" onClick={() => copiar(nova.chave)}>Copiar</button></p>
          <button type="button" onClick={() => setNova(null)}>Já guardei, fechar</button>
        </Alerta>
      )}
      {carregando ? <Carregando /> : (dados ?? []).length === 0 ? <p className="muted">Nenhuma chave emitida ainda.</p> : (
        <ul className="lista-chaves">
          {dados.map((k) => (
            <li key={k.id}>
              <span><b>{k.nome}</b> · {k.squad} · <code>{k.prefixo}…</code></span>
              <span className="muted pequeno">criada {dataHora(k.created_at)}{k.last_used_at ? ` · usada ${dataHora(k.last_used_at)}` : ' · nunca usada'}</span>
              {k.revoked_at ? <Selo tom="info">Revogada</Selo> : <button type="button" className="perigo" onClick={() => revogar(k)}>Revogar</button>}
            </li>
          ))}
        </ul>
      )}
    </article>
  );
}

export default function Integracoes() {
  const { equipe } = useAuth();
  const status = useCarga(() => api('/integrations/status'), []);
  const config = useCarga(() => (equipe ? api('/settings/integrations') : Promise.resolve([])), [equipe]);
  const [aba, setAba] = useState('wms');
  const recarregar = () => { status.recarregar(); config.recarregar(); };
  const porSquad = Object.fromEntries((config.dados ?? []).map((c) => [c.squad, c]));
  const lista = status.dados ?? [];
  const atual = aba === 'nossa' ? null : lista.find((x) => x.squad === aba) ?? lista[0];

  return (
    <div className="pagina">
      <Voltar para="/" />
      <Cabecalho titulo="Integrações" subtitulo="Uma aba por squad da plataforma SIG-Log: o que cada um informa dentro deste portal." />
      <Alerta tipo="info">
        {equipe
          ? <><b>Segurança:</b> a chave é enviada ao servidor, guardada cifrada e <b>nunca volta para o navegador</b>. Só o servidor a usa para chamar a API do outro squad. Ao configurar a URL, o portal deixa de usar dados simulados e passa a mostrar os dados reais.</>
          : <>Estas são as conexões do portal com os outros squads. Você vê os dados deles nos detalhes do <Link to="/pedidos">seu pedido</Link>.</>}
      </Alerta>
      <Alerta>{status.erro || config.erro}</Alerta>
      {status.carregando ? <Carregando /> : (
        <>
          <div className="abas" role="tablist" aria-label="Squads">
            {lista.map((x) => (
              <button key={x.squad} role="tab" type="button" aria-selected={atual?.squad === x.squad} className={atual?.squad === x.squad ? 'ativa' : ''}
                onClick={() => setAba(x.squad)}>{x.nome.split(' · ')[0].replace('Squad ', 'S')} {x.nome.split(' · ')[1].split(' ')[0]}</button>
            ))}
            {equipe && <button role="tab" type="button" aria-selected={aba === 'nossa'} className={aba === 'nossa' ? 'ativa' : ''} onClick={() => setAba('nossa')}>Nossa API</button>}
          </div>
          <div role="tabpanel" className="painel-aba">
            {aba === 'nossa' && equipe && <NossaApi />}
            {atual && <Aba status={atual} config={porSquad[atual.squad]} equipe={equipe} aoSalvar={recarregar} />}
          </div>
        </>
      )}
    </div>
  );
}
