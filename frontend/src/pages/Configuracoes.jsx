import { useState } from 'react';
import { api, apiBase, CHAVE_API_URL } from '../api.js';
import { Alerta, Cabecalho, Campo, Carregando, Selo } from '../components/ui.jsx';
import Icon from '../components/Icons.jsx';
import SeloEquipe from '../components/SeloEquipe.jsx';
import Voltar from '../components/Voltar.jsx';
import { useToast } from '../components/Toast.jsx';
import { useAuth } from '../auth.jsx';
import { useCarga } from '../hooks.js';
import { temDemo } from '../session.js';
import { dataHora } from '../lib.js';

const REPO = 'https://github.com/Anthonywilliam0102/siglog-customer';

function Conexao() {
  const { perfil } = useAuth();
  const toast = useToast();
  const padrao = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '');
  const [url, setUrl] = useState(() => { try { return localStorage.getItem(CHAVE_API_URL) || ''; } catch { return ''; } });
  const [teste, setTeste] = useState(null);

  async function testar() {
    const alvo = (url.trim() || padrao).replace(/\/$/, '');
    setTeste({ carregando: true });
    const t0 = performance.now();
    try {
      const r = await fetch(`${alvo}/health`);
      const d = await r.json();
      setTeste({ ok: r.ok, ms: Math.round(performance.now() - t0), servico: d.service });
    } catch {
      setTeste({ ok: false, erro: 'Não foi possível conectar. Confira a URL e se a API está no ar (no plano gratuito ela pode levar cerca de 1 minuto para acordar).' });
    }
  }
  function salvar() {
    const v = url.trim().replace(/\/$/, '');
    if (v && !/^https?:\/\//.test(v)) return toast.erro('Use uma URL completa, começando com https://');
    try { v ? localStorage.setItem(CHAVE_API_URL, v) : localStorage.removeItem(CHAVE_API_URL); } catch { /* sem storage */ }
    toast.ok(v ? 'URL da API salva. Recarregando…' : 'Voltou ao endereço padrão. Recarregando…');
    setTimeout(() => window.location.reload(), 700);
  }

  return (
    <div className="grade-config">
      <section className="cartao">
        <h2><Icon nome="plug" tamanho={20} /> API do sistema</h2>
        <p className="muted">Endereço usado por este navegador. Útil para apontar o portal para outra API (por exemplo, um túnel) sem refazer a publicação. Não altera o servidor.</p>
        {temDemo ? <Alerta tipo="info">No modo demonstração não há API para conectar.</Alerta> : (
          <>
            <p className="linha-info"><span>Em uso</span><code>{apiBase()}</code></p>
            <Campo label="Trocar a URL da API" ajuda={`Vazio = padrão do build (${padrao})`}>
              <input value={url} onChange={(e) => setUrl(e.target.value)} placeholder="https://minha-api.exemplo.com" inputMode="url" />
            </Campo>
            <div className="acoes esq">
              <button type="button" onClick={testar}><Icon nome="refresh" tamanho={16} /> Testar conexão</button>
              <button type="button" className="primario" onClick={salvar}>Salvar e recarregar</button>
            </div>
            {teste?.carregando && <Carregando texto="Testando…" />}
            {teste && !teste.carregando && (teste.ok
              ? <Alerta tipo="ok">Conectado ao serviço <b>{teste.servico}</b> em {teste.ms} ms.</Alerta>
              : <Alerta>{teste.erro ?? 'A API respondeu com erro.'}</Alerta>)}
          </>
        )}
      </section>
      <section className="cartao">
        <h2><Icon nome="shield" tamanho={20} /> Sua sessão</h2>
        <p className="linha-info"><span>Perfil</span><Selo tom="ok">{perfil.role}</Selo></p>
        <p className="linha-info"><span>Identificador</span><code>{perfil.sub}</code></p>
        <p className="muted">O perfil vem do login e é conferido pela API a cada pedido; esta tela apenas o exibe.</p>
      </section>
    </div>
  );
}

function Sobre() {
  return (
    <section className="cartao">
      <h2><Icon nome="info" tamanho={20} /> Sobre o sistema</h2>
      <p className="linha-info"><span>Produto</span>SIG-Log Customer · CRM, SAC &amp; Portal do Cliente (Squad 06)</p>
      <p className="linha-info"><span>Versão</span>1.0.0</p>
      <p className="linha-info"><span>API</span><code>{temDemo ? 'simulada no navegador' : apiBase()}</code></p>
      <div className="acoes esq">
        {!temDemo && <a className="botao" href={`${apiBase()}/docs`} target="_blank" rel="noreferrer"><Icon nome="link" tamanho={16} /> Documentação da API</a>}
        <a className="botao" href={REPO} target="_blank" rel="noreferrer"><Icon nome="link" tamanho={16} /> Código no GitHub</a>
      </div>
      <SeloEquipe />
    </section>
  );
}

const ABAS = [['conexao', 'Conexão', 'plug'], ['sobre', 'Sobre', 'info']];

export default function Configuracoes() {
  const [aba, setAba] = useState('conexao');
  return (
    <div className="pagina">
      <Voltar para="/" />
      <Cabecalho titulo="Configurações" subtitulo="Conexão com a API deste navegador e informações do sistema. As integrações com os outros squads ficam no menu da conta." />
      <div className="abas" role="tablist" aria-label="Seções de configuração">
        {ABAS.map(([id, nome, icone]) => (
          <button key={id} role="tab" type="button" id={`aba-${id}`} aria-selected={aba === id} aria-controls={`painel-${id}`}
            className={aba === id ? 'ativa' : ''} onClick={() => setAba(id)}><Icon nome={icone} tamanho={16} /> {nome}</button>
        ))}
      </div>
      <div role="tabpanel" id={`painel-${aba}`} aria-labelledby={`aba-${aba}`} className="painel-aba">
        {aba === 'conexao' && <Conexao />}
        {aba === 'sobre' && <Sobre />}
      </div>
    </div>
  );
}
