import os
import random
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from rpg_data import (
    create_player,
    get_player,
    update_player,
    add_xp,
    add_item,
    remove_item,
    equip_item,
    CLASSES,
    ENEMIES,
    ITEMS,
    use_item,
    modify_player_attribute,
    can_use_item,
    upgrade_weapon,
    LOCATIONS,
)

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Verifica se o token está presente
token = os.getenv("DISCORD_TOKEN")
if not token:
    print("Erro: Token do Discord não encontrado no arquivo .env")
    exit(1)

# Define as intenções do bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Habilita acesso aos membros do servidor
intents.presences = True  # Habilita acesso às presenças

# Cria uma instância do bot com o prefixo '!'
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"{bot.user} está online e pronto!")
    try:
        synced = await bot.tree.sync()
        print(f"Sincronizado {len(synced)} comando(s) slash")
    except Exception as e:
        print(f"Erro ao sincronizar comandos slash: {e}")


# Comandos com prefixo (!)
@bot.command(name="ola")
async def ola_prefix(ctx):
    """Comando com prefixo que responde com uma saudação"""
    await ctx.send(f"Olá {ctx.author.name}! Tudo bem?")


@bot.command(name="ping")
async def ping_prefix(ctx):
    """Comando com prefixo para verificar a latência do bot"""
    latency = round(bot.latency * 1000)
    await ctx.send(f"Pong! Latência: {latency}ms")


@bot.command(name="clear")
@commands.has_permissions(manage_messages=True)
async def clear_prefix(ctx, quantidade: int):
    """
    Comando com prefixo para limpar mensagens do chat
    Uso: !clear <quantidade>
    """
    if quantidade <= 0:
        await ctx.send("Por favor, especifique um número maior que 0.")
        return

    if quantidade > 100:
        await ctx.send("Você só pode limpar até 100 mensagens de uma vez.")
        return

    try:
        # +1 para incluir o comando de limpar
        deleted = await ctx.channel.purge(limit=quantidade + 1)
        await ctx.send(f"✅ {len(deleted)-1} mensagens foram apagadas!", delete_after=5)
    except discord.Forbidden:
        await ctx.send("Não tenho permissão para apagar mensagens neste canal.")
    except discord.HTTPException:
        await ctx.send("Ocorreu um erro ao tentar apagar as mensagens.")


# Comandos RPG com prefixo (!)
@bot.command(name="criar")
async def criar_personagem(ctx, classe: str):
    """Cria um novo personagem RPG"""
    try:
        player = create_player(str(ctx.author.id), ctx.author.name, classe)
        embed = discord.Embed(
            title="🎮 Personagem Criado!",
            description=f"Bem-vindo ao mundo de RPG, {ctx.author.name}!",
            color=discord.Color.green(),
        )
        embed.add_field(name="Classe", value=player["classe"].capitalize(), inline=True)
        embed.add_field(name="Nível", value=player["nivel"], inline=True)
        embed.add_field(name="HP", value=player["hp"], inline=True)
        embed.add_field(name="MP", value=player["mp"], inline=True)
        embed.add_field(name="Força", value=player["forca"], inline=True)
        embed.add_field(name="Defesa", value=player["defesa"], inline=True)
        embed.add_field(name="Magia", value=player["magia"], inline=True)
        embed.add_field(name="Velocidade", value=player["velocidade"], inline=True)
        await ctx.send(embed=embed)
    except ValueError as e:
        await ctx.send(f"Erro: {str(e)}")


@bot.command(name="status")
async def status(ctx):
    """Mostra o status do seu personagem"""
    player = get_player(str(ctx.author.id))
    if not player:
        await ctx.send("Você ainda não criou um personagem! Use !criar <classe>")
        return

    embed = discord.Embed(
        title=f"🎮 Status de {player['nome']}", color=discord.Color.blue()
    )
    embed.add_field(name="Classe", value=player["classe"].capitalize(), inline=True)
    embed.add_field(name="Nível", value=player["nivel"], inline=True)
    embed.add_field(
        name="XP", value=f"{player['xp']}/{player['xp_necessario']}", inline=True
    )
    embed.add_field(name="Gold", value=player["gold"], inline=True)
    embed.add_field(name="HP", value=player["hp"], inline=True)
    embed.add_field(name="MP", value=player["mp"], inline=True)
    embed.add_field(name="Força", value=player["forca"], inline=True)
    embed.add_field(name="Defesa", value=player["defesa"], inline=True)
    embed.add_field(name="Magia", value=player["magia"], inline=True)
    embed.add_field(name="Velocidade", value=player["velocidade"], inline=True)

    if player["equipamentos"]["arma"]:
        embed.add_field(
            name="Arma", value=player["equipamentos"]["arma"].capitalize(), inline=True
        )
    if player["equipamentos"]["armadura"]:
        embed.add_field(
            name="Armadura",
            value=player["equipamentos"]["armadura"].capitalize(),
            inline=True,
        )

    await ctx.send(embed=embed)


@bot.command(name="inventario")
async def inventario(ctx):
    """Mostra seu inventário"""
    player = get_player(str(ctx.author.id))
    if not player:
        await ctx.send("Você ainda não criou um personagem! Use !criar <classe>")
        return

    embed = discord.Embed(
        title=f"🎒 Inventário de {player['nome']}", color=discord.Color.gold()
    )

    if not player["inventario"]:
        embed.description = "Seu inventário está vazio!"
    else:
        for i, item in enumerate(player["inventario"], 1):
            # Remove o nível do nome do item para buscar no dicionário
            base_item = item.split("+")[0].lower()
            item_data = ITEMS[base_item]

            # Adiciona informações extras para armas
            if item_data["tipo"] == "arma":
                nivel = int(item.split("+")[1]) if "+" in item else 1
                embed.add_field(
                    name=f"{i}. {item.capitalize()}",
                    value=f"Tipo: {item_data['tipo']}\n"
                    f"Preço: {item_data['preço']} gold\n"
                    f"Dano: {item_data['dano']}\n"
                    f"Nível: {nivel}/{item_data['max_nivel']}\n"
                    f"Custo próximo upgrade: {item_data['custo_upgrade'] * nivel} gold",
                    inline=True,
                )
            else:
                embed.add_field(
                    name=f"{i}. {item.capitalize()}",
                    value=f"Tipo: {item_data['tipo']}\n"
                    f"Preço: {item_data['preço']} gold\n"
                    f"Efeito: Recupera {item_data['valor']} {item_data['efeito'].upper()}",
                    inline=True,
                )

    await ctx.send(embed=embed)


@bot.command(name="equipar")
async def equipar(ctx, numero: int):
    """
    Equipa um item do seu inventário usando seu número
    Uso: !equipar <número>
    """
    player = get_player(str(ctx.author.id))
    if not player:
        await ctx.send("Você ainda não criou um personagem! Use !criar <classe>")
        return

    if not player["inventario"]:
        await ctx.send("Seu inventário está vazio!")
        return

    try:
        if numero < 1 or numero > len(player["inventario"]):
            await ctx.send(
                f"Por favor, escolha um número entre 1 e {len(player['inventario'])}."
            )
            return

        item = player["inventario"][numero - 1]
        try:
            equip_item(str(ctx.author.id), item)
            await ctx.send(f"✅ {item.capitalize()} equipado com sucesso!")
        except ValueError as e:
            await ctx.send(f"Erro: {str(e)}")
    except ValueError:
        await ctx.send(
            "Por favor, especifique um número válido.\nUso: !equipar <número>"
        )


@bot.command(name="hunt")
async def hunt(ctx):
    """Inicia uma batalha com um inimigo aleatório"""
    player = get_player(str(ctx.author.id))
    if not player:
        await ctx.send("Você ainda não criou um personagem! Use !criar <classe>")
        return

    # Seleciona um inimigo aleatório
    enemy_name = random.choice(list(ENEMIES.keys()))
    enemy = ENEMIES[enemy_name]

    embed = discord.Embed(
        title="⚔️ Batalha Iniciada!",
        description=f"Um {enemy_name.capitalize()} selvagem apareceu!",
        color=discord.Color.red(),
    )
    embed.add_field(name="HP", value=enemy["hp"], inline=True)
    embed.add_field(name="Força", value=enemy["forca"], inline=True)
    embed.add_field(name="Defesa", value=enemy["defesa"], inline=True)

    message = await ctx.send(embed=embed)

    # Adiciona reações para as ações
    await message.add_reaction("⚔️")
    await message.add_reaction("🛡️")
    await message.add_reaction("🔮")
    await message.add_reaction("🏃")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["⚔️", "🛡️", "🔮", "🏃"]

    try:
        reaction, user = await bot.wait_for("reaction_add", timeout=30.0, check=check)

        if str(reaction.emoji) == "🏃":
            await ctx.send("Você fugiu da batalha!")
            return

        # Calcula o dano
        if str(reaction.emoji) == "⚔️":
            dano = max(1, player["forca"] - enemy["defesa"])
            player["hp"] -= max(1, enemy["forca"] - player["defesa"])
        elif str(reaction.emoji) == "🔮":
            if player["mp"] < 10:
                await ctx.send("MP insuficiente!")
                return
            dano = max(1, player["magia"] - enemy["defesa"])
            player["mp"] -= 10
            player["hp"] -= max(1, enemy["forca"] - player["defesa"])
        else:  # Defesa
            dano = 0
            player["hp"] -= max(1, (enemy["forca"] - player["defesa"]) // 2)

        enemy["hp"] -= dano

        # Atualiza o embed com o resultado
        embed = discord.Embed(
            title="⚔️ Resultado da Batalha", color=discord.Color.orange()
        )
        embed.add_field(name="Seu HP", value=player["hp"], inline=True)
        embed.add_field(
            name=f"HP do {enemy_name.capitalize()}", value=enemy["hp"], inline=True
        )
        embed.add_field(name="Dano causado", value=dano, inline=True)

        if enemy["hp"] <= 0:
            embed.description = f"Você derrotou o {enemy_name.capitalize()}!"
            embed.color = discord.Color.green()

            # Recompensas
            player["gold"] += enemy["gold"]
            add_xp(str(ctx.author.id), enemy["xp"])

            # Chance de drop de item
            if random.random() < 0.3:  # 30% de chance
                item = random.choice(list(ITEMS.keys()))
                add_item(str(ctx.author.id), item)
                embed.add_field(
                    name="🎁 Item Dropado", value=item.capitalize(), inline=False
                )

            embed.add_field(name="Gold ganho", value=enemy["gold"], inline=True)
            embed.add_field(name="XP ganho", value=enemy["xp"], inline=True)

        elif player["hp"] <= 0:
            embed.description = "Você foi derrotado!"
            embed.color = discord.Color.red()
            # Reseta o HP do jogador
            player["hp"] = CLASSES[player["classe"]]["hp"]

        update_player(str(ctx.author.id), player)
        await ctx.send(embed=embed)

    except TimeoutError:
        await ctx.send("Tempo esgotado! A batalha foi cancelada.")


@bot.command(name="loja")
async def loja(ctx):
    """Mostra os itens disponíveis na loja"""
    player = get_player(str(ctx.author.id))
    if not player:
        await ctx.send("Você ainda não criou um personagem! Use !criar <classe>")
        return

    # Cria um embed principal
    embed = discord.Embed(
        title="🏪 Loja de Itens",
        description=f"Use `!comprar <número>` para comprar um item\nUse `!vender <número>` para vender um item do seu inventário\n\nSeu gold atual: {player['gold']}\nSua classe: {player['classe'].capitalize()}",
        color=discord.Color.gold(),
    )

    # Lista todos os itens em ordem
    item_index = 0
    for item, dados in ITEMS.items():
        item_index += 1

        if dados["tipo"] == "consumível":
            valor = f"{item_index}. {item.capitalize()} - {dados['preço']} gold (Recupera {dados['valor']} {dados['efeito'].upper()})"
        else:  # Armas
            # Verifica se o jogador pode usar a arma
            pode_usar = can_use_item(player["classe"], item)
            status = "✅" if pode_usar else "❌"

            # Adiciona informações extras para armas
            raridade = dados.get("raridade", "comum").capitalize()
            classes = ", ".join(dados.get("classes", [])).capitalize()

            # Verifica se o jogador tem gold suficiente
            tem_gold = player["gold"] >= dados["preço"]
            status_gold = "✅" if tem_gold else "❌"

            valor = (
                f"{item_index}. {item.capitalize()} - {dados['preço']} gold {status_gold}\n"
                f"   Dano: {dados['dano']} | Raridade: {raridade}\n"
                f"   Classes: {classes} | Status: {status}\n"
                f"   {dados.get('descrição', '')}"
            )

        embed.add_field(name="\u200b", value=valor, inline=False)

    await ctx.send(embed=embed)


@bot.command(name="comprar")
async def comprar(ctx, numero: int):
    """
    Compra um item da loja
    Uso: !comprar <número>
    """
    player = get_player(str(ctx.author.id))
    if not player:
        await ctx.send("Você ainda não criou um personagem! Use !criar <classe>")
        return

    # Encontra o item pelo número
    item_index = 0
    item_encontrado = None
    for item, dados in ITEMS.items():
        item_index += 1
        if item_index == numero:
            item_encontrado = (item, dados)
            break

    if not item_encontrado:
        await ctx.send("Item não encontrado na loja!")
        return

    item, dados = item_encontrado

    # Verifica se o jogador pode usar o item
    if not can_use_item(player["classe"], item):
        embed = discord.Embed(
            title="❌ Erro ao Comprar",
            description=f"Você não pode usar este item!",
            color=discord.Color.red(),
        )
        embed.add_field(
            name="Sua Classe", value=player["classe"].capitalize(), inline=True
        )
        embed.add_field(
            name="Classes Permitidas",
            value=", ".join(dados.get("classes", [])).capitalize(),
            inline=True,
        )
        embed.add_field(
            name="Debug Info",
            value=f"Classe do jogador: '{player['classe']}'\nClasses do item: {dados.get('classes', [])}\nTipo do item: {dados['tipo']}",
            inline=False,
        )
        await ctx.send(embed=embed)
        return

    # Verifica se o jogador tem gold suficiente
    if player["gold"] < dados["preço"]:
        await ctx.send(
            f"Você não tem gold suficiente! Preço: {dados['preço']} gold\nSeu gold atual: {player['gold']}"
        )
        return

    # Compra o item
    player["gold"] -= dados["preço"]
    add_item(str(ctx.author.id), item)
    update_player(str(ctx.author.id), player)

    embed = discord.Embed(
        title="🛍️ Compra Realizada!",
        description=f"Você comprou {item.capitalize()} por {dados['preço']} gold",
        color=discord.Color.green(),
    )
    embed.add_field(name="Gold restante", value=player["gold"], inline=True)

    # Adiciona informações extras para armas
    if dados["tipo"] == "arma":
        embed.add_field(name="Dano", value=dados["dano"], inline=True)
        embed.add_field(
            name="Raridade",
            value=dados.get("raridade", "comum").capitalize(),
            inline=True,
        )
        embed.add_field(
            name="Descrição", value=dados.get("descrição", ""), inline=False
        )

    await ctx.send(embed=embed)


@bot.command(name="vender")
async def vender(ctx, numero: int):
    """
    Vende um item do seu inventário
    Uso: !vender <número>
    """
    player = get_player(str(ctx.author.id))
    if not player:
        await ctx.send("Você ainda não criou um personagem! Use !criar <classe>")
        return

    if not player["inventario"]:
        await ctx.send("Seu inventário está vazio!")
        return

    try:
        if numero < 1 or numero > len(player["inventario"]):
            await ctx.send(
                f"Por favor, escolha um número entre 1 e {len(player['inventario'])}."
            )
            return

        item = player["inventario"][numero - 1]
        preco_venda = ITEMS[item]["preço"] // 2  # Vende por metade do preço

        # Remove o item e adiciona o gold
        remove_item(str(ctx.author.id), item)
        player["gold"] += preco_venda
        update_player(str(ctx.author.id), player)

        embed = discord.Embed(
            title="💰 Venda Realizada!",
            description=f"Você vendeu {item.capitalize()} por {preco_venda} gold",
            color=discord.Color.green(),
        )
        embed.add_field(name="Gold atual", value=player["gold"], inline=True)
        await ctx.send(embed=embed)

    except ValueError:
        await ctx.send(
            "Por favor, especifique um número válido.\nUso: !vender <número>"
        )


@bot.command(name="usar")
async def usar(ctx, numero: int):
    """
    Usa um item consumível do seu inventário
    Uso: !usar <número>
    """
    player = get_player(str(ctx.author.id))
    if not player:
        await ctx.send("Você ainda não criou um personagem! Use !criar <classe>")
        return

    if not player["inventario"]:
        await ctx.send("Seu inventário está vazio!")
        return

    try:
        if numero < 1 or numero > len(player["inventario"]):
            await ctx.send(
                f"Por favor, escolha um número entre 1 e {len(player['inventario'])}."
            )
            return

        item = player["inventario"][numero - 1]
        sucesso, mensagem = use_item(str(ctx.author.id), item)

        if sucesso:
            embed = discord.Embed(
                title="✨ Item Usado!",
                description=f"Você usou {item.capitalize()}",
                color=discord.Color.green(),
            )
            embed.add_field(name="Efeito", value=mensagem, inline=True)
            embed.add_field(name="HP Atual", value=player["hp"], inline=True)
            embed.add_field(name="MP Atual", value=player["mp"], inline=True)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"Erro: {mensagem}")

    except ValueError:
        await ctx.send("Por favor, especifique um número válido.\nUso: !usar <número>")


@bot.command(name="modificar")
@commands.has_permissions(administrator=True)
async def modificar(ctx, membro: discord.Member, atributo: str, valor: int):
    """
    Comando administrativo para modificar atributos de um jogador
    Uso: !modificar @membro <atributo> <valor>
    Atributos disponíveis: hp, mp, forca, defesa, magia, velocidade, gold, xp, nivel
    """
    try:
        sucesso, mensagem = modify_player_attribute(str(membro.id), atributo, valor)

        if sucesso:
            embed = discord.Embed(
                title="⚙️ Atributo Modificado",
                description=f"Administrador: {ctx.author.name}",
                color=discord.Color.blue(),
            )
            embed.add_field(name="Jogador", value=membro.name, inline=True)
            embed.add_field(name="Atributo", value=atributo.upper(), inline=True)
            embed.add_field(name="Novo Valor", value=valor, inline=True)

            # Mostra o status atual do jogador
            player = get_player(str(membro.id))
            if player:
                embed.add_field(name="HP", value=player["hp"], inline=True)
                embed.add_field(name="MP", value=player["mp"], inline=True)
                embed.add_field(name="Nível", value=player["nivel"], inline=True)
                embed.add_field(name="Gold", value=player["gold"], inline=True)

            await ctx.send(embed=embed)
        else:
            await ctx.send(f"Erro: {mensagem}")

    except ValueError:
        await ctx.send("Por favor, especifique um valor numérico válido.")


@modificar.error
async def modificar_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Você não tem permissão para usar este comando.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "Uso correto: !modificar @membro <atributo> <valor>\n"
            "Atributos disponíveis: hp, mp, forca, defesa, magia, velocidade, gold, xp, nivel"
        )
    elif isinstance(error, commands.BadArgument):
        await ctx.send(
            "Argumento inválido. Certifique-se de mencionar um membro válido."
        )


# Comandos slash (/)
@bot.tree.command(name="ola", description="O bot responde com uma saudação")
async def ola_slash(interaction: discord.Interaction):
    """Comando slash que responde com uma saudação"""
    await interaction.response.send_message(f"Olá {interaction.user.name}! Tudo bem?")


@bot.tree.command(name="ping", description="Mostra a latência do bot")
async def ping_slash(interaction: discord.Interaction):
    """Comando slash para verificar a latência do bot"""
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"Pong! Latência: {latency}ms")


@bot.tree.command(name="limpar", description="Limpa mensagens do chat")
@app_commands.describe(quantidade="Quantidade de mensagens para apagar (máximo 100)")
@app_commands.checks.has_permissions(manage_messages=True)
async def limpar_slash(interaction: discord.Interaction, quantidade: int):
    """Comando slash para limpar mensagens do chat"""
    if quantidade <= 0:
        await interaction.response.send_message(
            "Por favor, especifique um número maior que 0.", ephemeral=True
        )
        return

    if quantidade > 100:
        await interaction.response.send_message(
            "Você só pode limpar até 100 mensagens de uma vez.", ephemeral=True
        )
        return

    try:
        await interaction.response.defer(ephemeral=True)
        # +1 para incluir o comando de limpar
        deleted = await interaction.channel.purge(limit=quantidade + 1)
        await interaction.followup.send(
            f"✅ {len(deleted)-1} mensagens foram apagadas!", ephemeral=True
        )
    except discord.Forbidden:
        await interaction.followup.send(
            "Não tenho permissão para apagar mensagens neste canal.", ephemeral=True
        )
    except discord.HTTPException:
        await interaction.followup.send(
            "Ocorreu um erro ao tentar apagar as mensagens.", ephemeral=True
        )


# Tratamento de erros para comandos com prefixo
@clear_prefix.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Você não tem permissão para usar este comando.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "Por favor, especifique quantas mensagens deseja apagar.\nUso: !clear <quantidade>"
        )
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Por favor, especifique um número válido.")


@bot.command(name="upgrade")
async def upgrade(ctx, numero: int):
    """
    Faz upgrade de uma arma do seu inventário
    Uso: !upgrade <número>
    """
    player = get_player(str(ctx.author.id))
    if not player:
        await ctx.send("Você ainda não criou um personagem! Use !criar <classe>")
        return

    if not player["inventario"]:
        await ctx.send("Seu inventário está vazio!")
        return

    try:
        if numero < 1 or numero > len(player["inventario"]):
            await ctx.send(
                f"Por favor, escolha um número entre 1 e {len(player['inventario'])}."
            )
            return

        item = player["inventario"][numero - 1]
        sucesso, mensagem = upgrade_weapon(str(ctx.author.id), item)

        if sucesso:
            embed = discord.Embed(
                title="⚡ Upgrade Realizado!",
                description=f"Você melhorou {item.capitalize()}",
                color=discord.Color.gold(),
            )
            embed.add_field(name="Resultado", value=mensagem, inline=True)
            embed.add_field(name="Gold restante", value=player["gold"], inline=True)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"Erro: {mensagem}")

    except ValueError:
        await ctx.send(
            "Por favor, especifique um número válido.\nUso: !upgrade <número>"
        )


@bot.command(name="locais")
async def locais(ctx):
    """Mostra os locais disponíveis para batalha"""
    player = get_player(str(ctx.author.id))
    if not player:
        await ctx.send("Você ainda não criou um personagem! Use !criar <classe>")
        return

    embed = discord.Embed(
        title="🗺️ Locais de Batalha",
        description="Use `!explorar <número>` para iniciar uma batalha",
        color=discord.Color.blue(),
    )

    for i, (local_id, local) in enumerate(LOCATIONS.items(), 1):
        status = "✅" if player["nivel"] >= local["nivel_minimo"] else "❌"

        # Divide as informações em campos menores
        embed.add_field(
            name=f"{i}. {status} {local['nome']}",
            value=f"Nível mínimo: {local['nivel_minimo']}",
            inline=False,
        )

        embed.add_field(
            name="Descrição",
            value=local["descrição"],
            inline=False,
        )

        embed.add_field(
            name="Recompensas",
            value=f"Gold base: {local['recompensa_base']}\n"
            f"XP base: {local['xp_base']}\n"
            f"Chance de item: {int(local['chance_item'] * 100)}%",
            inline=True,
        )

        embed.add_field(
            name="Inimigos",
            value=", ".join(local["inimigos"]).capitalize(),
            inline=True,
        )

    await ctx.send(embed=embed)


@bot.command(name="explorar")
async def explorar(ctx, numero: int):
    """
    Explora um local e inicia uma batalha
    Uso: !explorar <número>
    """
    player = get_player(str(ctx.author.id))
    if not player:
        await ctx.send("Você ainda não criou um personagem! Use !criar <classe>")
        return

    # Encontra o local pelo número
    local_encontrado = None
    for i, (local_id, local) in enumerate(LOCATIONS.items(), 1):
        if i == numero:
            local_encontrado = (local_id, local)
            break

    if not local_encontrado:
        await ctx.send(
            "Local não encontrado! Use !locais para ver os locais disponíveis."
        )
        return

    local_id, local_data = local_encontrado

    if player["nivel"] < local_data["nivel_minimo"]:
        await ctx.send(
            f"Você precisa ser nível {local_data['nivel_minimo']} para explorar este local!"
        )
        return

    # Seleciona um inimigo aleatório do local
    enemy_name = random.choice(local_data["inimigos"])
    enemy = ENEMIES[enemy_name].copy()

    # Ajusta os atributos do inimigo baseado no nível do jogador
    nivel_diferenca = player["nivel"] - local_data["nivel_minimo"]
    for attr in ["hp", "mp", "forca", "defesa", "magia"]:
        enemy[attr] = int(enemy[attr] * (1 + nivel_diferenca * 0.1))

    # Guarda o HP máximo do inimigo para mostrar a barra de vida
    enemy_max_hp = enemy["hp"]

    embed = discord.Embed(
        title=f"⚔️ Batalha em {local_data['nome']}!",
        description=f"Um {enemy_name.capitalize()} apareceu!\n{enemy['descrição']}",
        color=discord.Color.red(),
    )
    embed.add_field(name="HP", value=f"{enemy['hp']}/{enemy_max_hp}", inline=True)
    embed.add_field(name="Força", value=enemy["forca"], inline=True)
    embed.add_field(name="Defesa", value=enemy["defesa"], inline=True)

    message = await ctx.send(embed=embed)

    # Adiciona reações para as ações
    await message.add_reaction("⚔️")  # Ataque
    await message.add_reaction("🛡️")  # Defesa
    await message.add_reaction("🔮")  # Magia
    await message.add_reaction("🏃")  # Fugir

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["⚔️", "🛡️", "🔮", "🏃"]

    # Loop de batalha
    while True:
        try:
            reaction, user = await bot.wait_for(
                "reaction_add", timeout=30.0, check=check
            )

            if str(reaction.emoji) == "🏃":
                await ctx.send("Você fugiu da batalha!")
                return

            # Calcula o dano
            if str(reaction.emoji) == "⚔️":
                # Adiciona o bônus de dano da arma ao dano base
                dano = max(
                    1, (player["forca"] + player.get("dano_bonus", 0)) - enemy["defesa"]
                )
                player["hp"] -= max(1, enemy["forca"] - player["defesa"])
                acao = "ataque físico"
            elif str(reaction.emoji) == "🔮":
                if player["mp"] < 10:
                    await ctx.send("MP insuficiente!")
                    continue
                dano = max(1, player["magia"] - enemy["defesa"])
                player["mp"] -= 10
                player["hp"] -= max(1, enemy["forca"] - player["defesa"])
                acao = "ataque mágico"
            else:  # Defesa
                dano = 0
                player["hp"] -= max(1, (enemy["forca"] - player["defesa"]) // 2)
                acao = "defesa"

            enemy["hp"] -= dano

            # Atualiza o embed com o resultado
            embed = discord.Embed(
                title="⚔️ Batalha em Andamento",
                description=f"Você usou {acao}!",
                color=discord.Color.orange(),
            )

            # Adiciona informações de dano em campos separados
            embed.add_field(
                name="Dano Causado",
                value=f"{dano}",
                inline=True,
            )
            embed.add_field(
                name="Dano Recebido",
                value=f"{max(1, enemy['forca'] - player['defesa'])}",
                inline=True,
            )

            # Adiciona barras de vida
            player_hp_percent = (player["hp"] / CLASSES[player["classe"]]["hp"]) * 100
            enemy_hp_percent = (enemy["hp"] / enemy_max_hp) * 100

            player_hp_bar = "█" * int(player_hp_percent / 10) + "░" * (
                10 - int(player_hp_percent / 10)
            )
            enemy_hp_bar = "█" * int(enemy_hp_percent / 10) + "░" * (
                10 - int(enemy_hp_percent / 10)
            )

            # Adiciona informações de HP em campos separados
            embed.add_field(
                name=f"Seu HP: {player['hp']}/{CLASSES[player['classe']]['hp']}",
                value=f"`{player_hp_bar}` {int(player_hp_percent)}%",
                inline=False,
            )
            embed.add_field(
                name=f"HP do {enemy_name.capitalize()}: {enemy['hp']}/{enemy_max_hp}",
                value=f"`{enemy_hp_bar}` {int(enemy_hp_percent)}%",
                inline=False,
            )

            # Verifica se alguém foi derrotado
            if enemy["hp"] <= 0:
                embed.description = f"Você derrotou o {enemy_name.capitalize()}!"
                embed.color = discord.Color.green()

                # Recompensas baseadas no local
                gold_ganho = local_data["recompensa_base"] + enemy["gold"]
                xp_ganho = local_data["xp_base"] + enemy["xp"]

                # Chance de drop de item
                if random.random() < local_data["chance_item"]:
                    item = random.choice(list(ITEMS.keys()))
                    add_item(str(ctx.author.id), item)
                    embed.add_field(
                        name="🎁 Item Dropado", value=item.capitalize(), inline=False
                    )

                # Adiciona recompensas
                player["gold"] += gold_ganho
                add_xp(str(ctx.author.id), xp_ganho)

                embed.add_field(name="Gold ganho", value=gold_ganho, inline=True)
                embed.add_field(name="XP ganho", value=xp_ganho, inline=True)

                update_player(str(ctx.author.id), player)
                await ctx.send(embed=embed)
                break

            elif player["hp"] <= 0:
                embed.description = "Você foi derrotado!"
                embed.color = discord.Color.red()
                # Reseta o HP do jogador
                player["hp"] = CLASSES[player["classe"]]["hp"]

                update_player(str(ctx.author.id), player)
                await ctx.send(embed=embed)
                break

            # Atualiza a mensagem com o novo estado da batalha
            await message.edit(embed=embed)

        except TimeoutError:
            await ctx.send("Tempo esgotado! A batalha foi cancelada.")
            break


@bot.command(name="ajuda")
async def ajuda(ctx, categoria: str = None):
    """
    Mostra todos os comandos disponíveis
    Uso: !ajuda [categoria]
    Categorias: basico, personagem, inventario, loja, batalha, upgrade, admin
    """
    categorias = {
        "basico": {
            "nome": "📚 Comandos Básicos",
            "comandos": {
                "!ola": "O bot responde com uma saudação",
                "!ping": "Mostra a latência do bot",
                "!clear <quantidade>": "Limpa mensagens do chat (requer permissão)",
            },
        },
        "personagem": {
            "nome": "🎮 Comandos de Personagem",
            "comandos": {
                "!criar <classe>": "Cria um novo personagem (guerreiro, mago, arqueiro)",
                "!status": "Mostra o status do seu personagem",
            },
        },
        "inventario": {
            "nome": "🎒 Comandos de Inventário",
            "comandos": {
                "!inventario": "Mostra seus itens",
                "!equipar <número>": "Equipa um item do inventário",
                "!usar <número>": "Usa um item consumível",
            },
        },
        "loja": {
            "nome": "🏪 Comandos da Loja",
            "comandos": {
                "!loja": "Mostra os itens disponíveis",
                "!comprar <número>": "Compra um item da loja",
                "!vender <número>": "Vende um item do inventário",
            },
        },
        "batalha": {
            "nome": "⚔️ Comandos de Batalha",
            "comandos": {
                "!locais": "Mostra os locais disponíveis para batalha",
                "!explorar <número>": "Inicia uma batalha no local escolhido",
                "!hunt": "Inicia uma batalha com um inimigo aleatório",
            },
        },
        "upgrade": {
            "nome": "⚡ Comandos de Upgrade",
            "comandos": {"!upgrade <número>": "Melhora uma arma do seu inventário"},
        },
        "admin": {
            "nome": "⚙️ Comandos Administrativos",
            "comandos": {
                "!modificar @membro <atributo> <valor>": "Modifica atributos de um jogador (requer permissão)"
            },
        },
    }

    if categoria and categoria.lower() in categorias:
        # Mostra apenas a categoria especificada
        cat = categorias[categoria.lower()]
        embed = discord.Embed(title=cat["nome"], color=discord.Color.blue())
        for comando, descricao in cat["comandos"].items():
            embed.add_field(name=comando, value=descricao, inline=False)
    else:
        # Mostra todas as categorias
        embed = discord.Embed(
            title="📚 Comandos do Bot",
            description="Use `!ajuda <categoria>` para ver comandos específicos\n"
            "Categorias: basico, personagem, inventario, loja, batalha, upgrade, admin",
            color=discord.Color.blue(),
        )
        for cat_id, cat in categorias.items():
            comandos = "\n".join([f"`{cmd}`" for cmd in cat["comandos"].keys()])
            embed.add_field(name=cat["nome"], value=comandos, inline=False)

    await ctx.send(embed=embed)


# Inicia o bot usando o token do arquivo .env
bot.run(token)
