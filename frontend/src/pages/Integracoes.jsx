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
  nao_prevista: ['info', 'Sem integração prevista'],
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

function Cartao({ status, config, equipe, aoSalvar }) {
  const [tom, rotulo] = MODOS[status.modo] ?? MODOS.nao_configurada;
  const editavel = equipe && status.modo !== 'nao_prevista' && config;
  return (
    <article className="cartao integracao" data-squad={status.squad}>
      <div className="integracao-topo">
        <h3>{status.nome}</h3>
        <Selo tom={tom}>{rotulo}</Selo>
      </div>
      <p className="muted">{status.funcao}</p>
      {status.modo === 'simulada' && <p className="pequeno muted">Enquanto o squad não conecta a API real, o portal mostra dados simulados, sempre identificados como tal.</p>}
      {editavel && <Formulario key={`${config.squad}-${config.atualizado_em}`} item={config} aoSalvar={aoSalvar} />}
    </article>
  );
}

export default function Integracoes() {
  const { equipe } = useAuth();
  const status = useCarga(() => api('/integrations/status'), []);
  const config = useCarga(() => (equipe ? api('/settings/integrations') : Promise.resolve([])), [equipe]);
  const recarregar = () => { status.recarregar(); config.recarregar(); };
  const porSquad = Object.fromEntries((config.dados ?? []).map((c) => [c.squad, c]));

  return (
    <div className="pagina">
      <Voltar para="/" />
      <Cabecalho titulo="Integrações" subtitulo="O que os outros squads da plataforma SIG-Log informam dentro deste portal." />
      <Alerta tipo="info">
        {equipe
          ? <><b>Segurança:</b> a chave é enviada ao servidor, guardada cifrada e <b>nunca volta para o navegador</b>. Só o servidor a usa para chamar a API do outro squad. Ao configurar a URL, o portal deixa de usar dados simulados e passa a mostrar os dados reais.</>
          : <>Estas são as conexões do portal com os outros squads. Você vê os dados deles nos detalhes do <Link to="/pedidos">seu pedido</Link>.</>}
      </Alerta>
      <Alerta>{status.erro || config.erro}</Alerta>
      {status.carregando ? <Carregando /> : (
        <div className="grade-integracoes">
          {(status.dados ?? []).map((s) => <Cartao key={s.squad} status={s} config={porSquad[s.squad]} equipe={equipe} aoSalvar={recarregar} />)}
        </div>
      )}
    </div>
  );
}
