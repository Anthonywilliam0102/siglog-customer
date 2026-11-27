import Icon from './Icons.jsx';

// Selo de autoria: aparece no rodapé do sistema e na tela de login.
export default function SeloEquipe({ className = '' }) {
  return (
    <span className={`selo-equipe ${className}`} title="Sistema produzido pela equipe Student Help">
      <span className="selo-equipe-icone"><Icon nome="cap" tamanho={16} /></span>
      <span>Produzido pela equipe <b>Student Help</b></span>
    </span>
  );
}
