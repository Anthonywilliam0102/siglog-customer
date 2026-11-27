import { Link } from 'react-router-dom';
import { Cabecalho, Selo } from '../components/ui.jsx';
import Icon from '../components/Icons.jsx';
import Voltar from '../components/Voltar.jsx';
import { useAuth } from '../auth.jsx';
import { dataHora } from '../lib.js';

// Mostra só o fim do documento (privacidade na tela).
function mascarar(doc, tipo) {
  const f = doc.slice(-2);
  return tipo === 'PF' ? `***.***.***-${f}` : `**.***.***/****-${f}`;
}

function Linha({ rotulo, children }) {
  return <p className="linha-info"><span>{rotulo}</span><span>{children}</span></p>;
}

export default function Conta() {
  const { perfil, equipe, cliente } = useAuth();
  return (
    <div className="pagina estreita">
      <Voltar para="/" />
      <Cabecalho titulo="Minha conta" subtitulo="Seus dados de cadastro e o seu acesso ao portal." />

      {cliente && (
        <section className="cartao">
          <h2><Icon nome="user" tamanho={20} /> Dados do cadastro</h2>
          <Linha rotulo="Nome">{cliente.nome}</Linha>
          <Linha rotulo="Tipo">{cliente.tipo === 'PF' ? 'Pessoa física' : 'Pessoa jurídica'}</Linha>
          <Linha rotulo={cliente.tipo === 'PF' ? 'CPF' : 'CNPJ'}><code>{mascarar(cliente.documento, cliente.tipo)}</code></Linha>
          <Linha rotulo="E-mail">{cliente.email}</Linha>
          {cliente.telefone && <Linha rotulo="Telefone">{cliente.telefone}</Linha>}
          {cliente.endereco && <Linha rotulo="Endereço">{cliente.endereco}</Linha>}
          <Linha rotulo="Cliente desde">{dataHora(cliente.created_at)}</Linha>
          <p className="muted">Para corrigir algum dado, <Link to="/chamados/novo">fale conosco</Link> e a equipe atualiza para você.</p>
        </section>
      )}

      <section className="cartao">
        <h2><Icon nome="shield" tamanho={20} /> Seu acesso</h2>
        <Linha rotulo="Perfil"><Selo tom="ok">{equipe ? perfil.role : 'cliente'}</Selo></Linha>
        <Linha rotulo="Identificador"><code>{perfil.sub}</code></Linha>
        <p className="muted">
          {equipe
            ? 'Você tem acesso de equipe: fila de atendimento, todos os pedidos e a tela de Configurações.'
            : 'Você enxerga apenas os seus próprios pedidos, chamados e sinistros.'}
        </p>
        {equipe && <div className="acoes esq"><Link className="botao" to="/configuracoes"><Icon nome="sliders" tamanho={16} /> Abrir Configurações</Link></div>}
      </section>
    </div>
  );
}
