# Portal do Cliente (frontend)

React 18 + Vite + React Router. Login pelo **Supabase Auth**; todos os dados vêm da API (`../openapi.yaml`), nunca direto do banco.

## Telas
| Rota | Quem | O que faz |
|---|---|---|
| `/login` | todos | e-mail e senha (Supabase) |
| `/cadastro` | cliente novo | completa o cadastro PF/PJ (valida CPF/CNPJ) |
| `/` | todos | atalhos e pedidos recentes |
| `/cotacao` | cliente / equipe | cotação e confirmação do pedido |
| `/pedidos`, `/pedidos/:id` | todos | lista com filtro, andamento, rastreamento, avaliação da entrega; equipe muda o status (RN07) |
| `/chamados`, `/chamados/novo`, `/chamados/:id` | todos | SAC: abrir, conversar, SLA, avaliar atendimento |
| `/sinistros`, `/sinistros/novo` | todos | registrar e acompanhar sinistros |
| `/atendimento` | equipe | fila de chamados por prazo de SLA |

O perfil (cliente, atendente, gestor) vem do token; o front só esconde opções, **a API é quem autoriza** (RN02).

## Design
Tokens de cor, raio e sombra em `src/styles.css` (`:root`, com tema escuro automático). Glassmorphism (`.vidro`) só em hero, login e estatísticas; tabelas e formulários ficam em fundo sólido para manter a leitura e o contraste. Animações respeitam `prefers-reduced-motion`. Ícones em SVG inline (`components/Icons.jsx`), sem dependência extra.

## Rodar
```bash
cd frontend
cp .env.example .env.local     # preencha VITE_SUPABASE_URL e VITE_SUPABASE_PUBLISHABLE_KEY
npm install && npm run dev     # http://localhost:5173 (proxy /api -> http://localhost:8000)
```
Sem as variáveis do Supabase, o login pede um **token de desenvolvimento** (`python scripts/gen_token.py <sub> cliente`).
Use apenas a chave **publishable**; nunca a `secret`/`service_role`.

## Rastreamento
Enquanto o squad Tracking não publica contrato, a API devolve um rastreamento **simulado** (`TRACKING_MOCK=true`), identificado na tela como "simulado (demonstração)".

## Produção (Cloudflare Pages)
Build: `npm run build` · diretório: `frontend` · saída: `dist` · variáveis: `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY`, `VITE_API_URL` (URL pública da API).
Na API, defina `CORS_ORIGINS=https://<seu-projeto>.pages.dev`.
