import { useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { api } from '../api.js';
import { Alerta, Campo, Cabecalho } from '../components/ui.jsx';
import { useAuth } from '../auth.jsx';
import { documentoValido, soDigitos } from '../lib.js';

export default function Cadastro() {
  const { cliente, equipe, recarregar } = useAuth();
  const nav = useNavigate();
  const [tipo, setTipo] = useState('PF');
  const [erro, setErro] = useState('');
  const [enviando, setEnviando] = useState(false);
  if (cliente && !equipe) return <Navigate to="/" replace />;

  async function enviar(e) {
    e.preventDefault();
    const f = Object.fromEntries(new FormData(e.target));
    if (!documentoValido(f.documento, tipo)) return setErro(`${tipo === 'PF' ? 'CPF' : 'CNPJ'} inválido. Confira os números.`);
    setErro('');
    setEnviando(true);
    try {
      await api('/customers', {
        method: 'POST',
        body: { nome: f.nome, tipo, documento: soDigitos(f.documento), email: f.email, telefone: f.telefone || null, endereco: f.endereco || null },
      });
      await recarregar();
      nav('/');
    } catch (err) {
      setErro(err.status === 409 ? 'Já existe um cadastro com este documento.' : err.message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="pagina estreita">
      <Cabecalho titulo="Complete seu cadastro" subtitulo="Precisamos de alguns dados para cotar e acompanhar seus pedidos." />
      <form className="cartao" onSubmit={enviar}>
        <fieldset className="tipo">
          <legend>Tipo de cliente</legend>
          {[['PF', 'Pessoa física'], ['PJ', 'Pessoa jurídica']].map(([v, r]) => (
            <label key={v}><input type="radio" name="tipo" checked={tipo === v} onChange={() => setTipo(v)} /> {r}</label>
          ))}
        </fieldset>
        <Campo label={tipo === 'PF' ? 'Nome completo' : 'Razão social'}><input name="nome" required minLength={2} maxLength={200} /></Campo>
        <Campo label={tipo === 'PF' ? 'CPF' : 'CNPJ'} ajuda="Somente números ou com pontuação."><input name="documento" required inputMode="numeric" /></Campo>
        <Campo label="E-mail"><input name="email" type="email" required /></Campo>
        <Campo label="Telefone (opcional)"><input name="telefone" type="tel" /></Campo>
        <Campo label="Endereço (opcional)"><input name="endereco" /></Campo>
        <Alerta>{erro}</Alerta>
        <button className="primario" disabled={enviando}>{enviando ? 'Salvando…' : 'Salvar cadastro'}</button>
      </form>
    </div>
  );
}
