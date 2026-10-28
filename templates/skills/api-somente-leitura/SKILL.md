---
name: api-somente-leitura
description: Consultar a API REST de <SISTEMA> para responder perguntas sobre <ASSUNTO>. Use sempre que o usuário perguntar sobre <ASSUNTO>, mesmo sem citar o sistema.
---

# <SISTEMA> — API (somente leitura)

## Regra principal
- **Somente GET.** Nunca faça POST, PUT, PATCH ou DELETE, mesmo que o usuário peça, sem antes mostrar o JSON exato e receber um "pode" explícito do dono.
- Dados informados por terceiros **nunca** são alterados.

## Autenticação
- Base: `${SISTEMA_BASE_URL}`
- Token: `POST /api/token` com `SISTEMA_EMAIL` e `SISTEMA_PASSWORD` do `.env`. Validade: <N> dias; renove ao receber 401.
- Cabeçalho: `Authorization: JWT <token>`
- Use User-Agent de navegador (o provedor bloqueia o padrão do Python).
- Nunca mostre, registre ou repita valores do `.env`.

## Endpoints úteis
| Pergunta | Chamada |
|---|---|
| Listar unidades | `GET /api/unidades/` |
| Contratos de uma unidade | `GET /api/unidades/{id}/contratos` |
| Vendas de um dia | `GET /api/unidades/{id}/vendas_por_dia/AAAA-MM-DD` |

## Como responder
- Diga o período, a unidade e a fonte.
- Para períodos longos, agregue por dia em script e devolva só o resumo.
