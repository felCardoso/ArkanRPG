# Bot do Discord

Este é um bot simples do Discord criado com Python.

## Configuração

1. Primeiro, instale as dependências necessárias:
```bash
pip install -r requirements.txt
```

2. Crie um bot no [Portal de Desenvolvedores do Discord](https://discord.com/developers/applications)
   - Crie uma nova aplicação
   - Vá para a seção "Bot"
   - Clique em "Add Bot"
   - Copie o token do bot

3. Configure o arquivo `.env`:
   - Abra o arquivo `.env`
   - Substitua `seu_token_aqui` pelo token do seu bot

4. Convide o bot para seu servidor:
   - No portal de desenvolvedores, vá para "OAuth2" > "URL Generator"
   - Selecione os escopos: `bot` e `applications.commands`
   - Selecione as permissões necessárias (recomendado: "Send Messages", "Read Messages/View Channels")
   - Use a URL gerada para convidar o bot para seu servidor

## Executando o Bot

Para iniciar o bot, execute:
```bash
python bot.py
```

## Comandos Disponíveis

- `!ola` - O bot responde com uma saudação
- `!ping` - Mostra a latência atual do bot 