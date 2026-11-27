import { useLocation, useNavigate } from 'react-router-dom';
import Icon from './Icons.jsx';

// Volta uma página no histórico; se a pessoa entrou direto nesta tela, vai para `para`.
export default function Voltar({ para = '/', rotulo = 'Voltar' }) {
  const nav = useNavigate();
  const loc = useLocation();
  return (
    <button type="button" className="voltar" onClick={() => (loc.key !== 'default' ? nav(-1) : nav(para))}>
      <Icon nome="back" tamanho={18} /> {rotulo}
    </button>
  );
}
