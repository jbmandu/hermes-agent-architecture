# Lições aprendidas

- **Skill sozinha não basta.** Uma regra só na skill às vezes não disparava; repetir a regra na memória persistente do agente resolveu.
- **WAF bloqueia o User-Agent padrão do Python.** Um provedor atrás de Cloudflare devolvia 403 (erro 1010); a skill passou a exigir User-Agent de navegador.
- **O agente corrompe código que redigita.** Para instalar um script, publicar o arquivo numa URL, baixar com `curl` e conferir o hash. Nunca colar código ou base64 no chat.
- **Chamadas longas morrem no túnel (~100 s).** Tarefas longas rodam em segundo plano e o resultado é consultado em chamadas curtas.
- **Botão de login que não é `submit`.** Scripts de portal clicam no botão e esperam a URL mudar, com o envio do formulário como plano B.
- **Especificação do usuário vem em camadas.** "Processo em PDF" significava o documento oficial do procedimento, não um print da tela. Perguntar o resultado esperado antes de automatizar.
- **Fuso horário.** Crons rodavam em UTC; definir `timezone` na configuração evitou relatório às 4h.
- **Processos fora do supervisor não sobrevivem a reinício.** Tudo que roda com `nohup` precisa de script de inicialização documentado.
- **Escolha de modelo com gabarito.** Um teste curto com respostas conhecidas decide melhor que impressões.
