# Segurança

## Modelo de ameaças

| Risco | Controle |
|---|---|
| Agente altera dado de sistema | Escopo de leitura no OAuth; ferramentas de escrita removidas em `config.yaml`; skills com regra GET-only; POST só com OK explícito |
| Usuário não autorizado fala com o agente | Lista de permitidos por canal (IDs Telegram, números WhatsApp, e-mails) |
| Endpoint público exposto | Caminho secreto por cliente, filtro por IP de origem, chave em cabeçalho, resposta 404 para tudo que não confere, log de acesso |
| Vazamento de credencial | Segredos só no `.env` do servidor; nunca em chat, prompt, skill ou repositório; agente instruído a não revelar valores |
| Código malicioso enviado ao agente | Código entregue por URL e conferido por hash (md5) antes de rodar; o agente lê antes de executar |
| Cota do modelo acaba | Modelo de fallback configurado |

## Defesa em camadas: por que não basta o prompt

Uma instrução como "nunca escreva no ERP" é a última camada, não a primeira. A ordem que adotei:

1. **Credencial** com o menor escopo que o fornecedor oferece (ex.: `bi.read`).
2. **Configuração**: ferramenta de escrita fora da lista (`tools.exclude`).
3. **Skill**: regra explícita do que pode e do que exige autorização.
4. **Memória do agente**: a mesma regra registrada, porque nem sempre a skill é acionada.

Quando o fornecedor não oferece usuário somente leitura, isso fica documentado como risco aceito e o pedido de usuário restrito é feito a ele.

## Túneis

- Túnel temporário (Cloudflare quick tunnel) para a API do agente: endereço muda a cada reinício; aceitável porque a API exige chave.
- Domínio fixo (ngrok) para a ponte MCP, porque os apps de IA precisam de URL estável. Alternativa mais robusta: túnel nomeado com controle de acesso.
