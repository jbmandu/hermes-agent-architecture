---
name: portal-web-sem-api
description: Ler valores e baixar documentos de <SISTEMA> que não estão na API, usando os scripts instalados. Use para indicadores, análises críticas e documentos oficiais.
---

# <SISTEMA> — acesso web (somente leitura)

## Regra principal
- **Sempre rode um dos scripts abaixo.** Nunca abra um navegador por conta própria nem peça para conectar um.
- Somente leitura: não clique em salvar, aprovar, excluir ou enviar.

## Scripts
| Tarefa | Comando |
|---|---|
| Valor de um indicador (meta x realizado) | `python scripts/portal_kpi.py <id ou nome>` |
| Buscar em qualquer módulo | `python scripts/portal_find.py <escopo> <termo>` |
| Documento oficial de um processo | `python scripts/portal_doc.py <id ou nome>` → salva .docx e .pdf |

Os scripts usam perfil de navegador persistente, refazem o login sozinhos quando a sessão expira e leem credenciais do `.env` (`PORTAL_EMAIL`, `PORTAL_PASSWORD`).

## Tarefas longas
Rode em segundo plano (`nohup ... > saida.txt &`) e leia o arquivo depois: chamadas longas caem no túnel.
