import { Navigate, Route, Routes, useLocation } from 'react-router-dom';
import Layout from './components/Layout.jsx';
import { Carregando } from './components/ui.jsx';
import { useAuth } from './auth.jsx';
import Login from './pages/Login.jsx';
import Home from './pages/Home.jsx';
import Cadastro from './pages/Cadastro.jsx';
import Cotacao from './pages/Cotacao.jsx';
import Pedidos from './pages/Pedidos.jsx';
import PedidoDetalhe from './pages/PedidoDetalhe.jsx';
import Chamados from './pages/Chamados.jsx';
import NovoChamado from './pages/NovoChamado.jsx';
import ChamadoDetalhe from './pages/ChamadoDetalhe.jsx';
import Sinistros from './pages/Sinistros.jsx';
import NovoSinistro from './pages/NovoSinistro.jsx';
import Atendimento from './pages/Atendimento.jsx';
import Configuracoes from './pages/Configuracoes.jsx';
import Conta from './pages/Conta.jsx';
import Integracoes from './pages/Integracoes.jsx';

function Protegido() {
  const { carregando, perfil, equipe, cliente } = useAuth();
  const { pathname } = useLocation();
  if (carregando) return <main><Carregando texto="Entrando…" /></main>;
  if (!perfil) return <Navigate to="/login" replace />;
  if (!equipe && !cliente && pathname !== '/cadastro') return <Navigate to="/cadastro" replace />;
  return <Layout />;
}

function SoEquipe({ children }) {
  const { equipe } = useAuth();
  return equipe ? children : <Navigate to="/" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<Protegido />}>
        <Route index element={<Home />} />
        <Route path="cadastro" element={<Cadastro />} />
        <Route path="cotacao" element={<Cotacao />} />
        <Route path="conta" element={<Conta />} />
        <Route path="integracoes" element={<Integracoes />} />
        <Route path="pedidos" element={<Pedidos />} />
        <Route path="pedidos/:id" element={<PedidoDetalhe />} />
        <Route path="chamados" element={<Chamados />} />
        <Route path="chamados/novo" element={<NovoChamado />} />
        <Route path="chamados/:id" element={<ChamadoDetalhe />} />
        <Route path="sinistros" element={<Sinistros />} />
        <Route path="sinistros/novo" element={<NovoSinistro />} />
        <Route path="atendimento" element={<SoEquipe><Atendimento /></SoEquipe>} />
        <Route path="configuracoes" element={<SoEquipe><Configuracoes /></SoEquipe>} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
