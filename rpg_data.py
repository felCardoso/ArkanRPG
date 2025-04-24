import json
import os
from typing import Dict, List, Optional

# Estrutura de dados para armazenar informações dos jogadores
players_data = {}

# Classes disponíveis
CLASSES = {
    "guerreiro": {
        "hp": 100,
        "mp": 20,
        "forca": 15,
        "defesa": 10,
        "magia": 5,
        "velocidade": 8,
    },
    "mago": {
        "hp": 60,
        "mp": 50,
        "forca": 5,
        "defesa": 5,
        "magia": 20,
        "velocidade": 10,
    },
    "arqueiro": {
        "hp": 80,
        "mp": 30,
        "forca": 10,
        "defesa": 7,
        "magia": 10,
        "velocidade": 15,
    },
}

# Locais de batalha
LOCATIONS = {
    "floresta": {
        "nome": "Floresta Encantada",
        "nivel_minimo": 1,
        "descrição": "Uma floresta mágica cheia de criaturas misteriosas",
        "inimigos": ["goblin", "lobo", "aranha"],
        "recompensa_base": 10,
        "xp_base": 15,
        "chance_item": 0.3,
    },
    "caverna": {
        "nome": "Caverna dos Orcs",
        "nivel_minimo": 5,
        "descrição": "Uma caverna escura habitada por orcs e trolls",
        "inimigos": ["orc", "troll", "goblin"],
        "recompensa_base": 25,
        "xp_base": 30,
        "chance_item": 0.4,
    },
    "montanha": {
        "nome": "Montanha do Dragão",
        "nivel_minimo": 10,
        "descrição": "Uma montanha onde dragões fazem seus ninhos",
        "inimigos": ["dragão", "grifo", "troll"],
        "recompensa_base": 50,
        "xp_base": 60,
        "chance_item": 0.5,
    },
    "ruínas": {
        "nome": "Ruínas Antigas",
        "nivel_minimo": 15,
        "descrição": "Ruínas de uma civilização antiga, guardada por criaturas mágicas",
        "inimigos": ["golem", "esqueleto", "fantasma"],
        "recompensa_base": 75,
        "xp_base": 90,
        "chance_item": 0.6,
    },
    "abismo": {
        "nome": "Abismo Profundo",
        "nivel_minimo": 20,
        "descrição": "Um abismo escuro onde criaturas demoníacas habitam",
        "inimigos": ["demônio", "dragão", "golem"],
        "recompensa_base": 100,
        "xp_base": 120,
        "chance_item": 0.7,
    },
}

# Inimigos disponíveis
ENEMIES = {
    "goblin": {
        "hp": 50,
        "mp": 10,
        "forca": 8,
        "defesa": 5,
        "magia": 3,
        "velocidade": 7,
        "xp": 10,
        "gold": 5,
        "descrição": "Um goblin pequeno e ágil",
    },
    "lobo": {
        "hp": 60,
        "mp": 0,
        "forca": 10,
        "defesa": 4,
        "magia": 0,
        "velocidade": 12,
        "xp": 12,
        "gold": 8,
        "descrição": "Um lobo selvagem e feroz",
    },
    "aranha": {
        "hp": 40,
        "mp": 0,
        "forca": 6,
        "defesa": 3,
        "magia": 0,
        "velocidade": 15,
        "xp": 8,
        "gold": 6,
        "descrição": "Uma aranha venenosa e rápida",
    },
    "orc": {
        "hp": 80,
        "mp": 15,
        "forca": 12,
        "defesa": 8,
        "magia": 5,
        "velocidade": 6,
        "xp": 20,
        "gold": 10,
        "descrição": "Um orc forte e resistente",
    },
    "troll": {
        "hp": 120,
        "mp": 20,
        "forca": 15,
        "defesa": 12,
        "magia": 8,
        "velocidade": 5,
        "xp": 30,
        "gold": 15,
        "descrição": "Um troll grande e poderoso",
    },
    "dragão": {
        "hp": 200,
        "mp": 50,
        "forca": 25,
        "defesa": 20,
        "magia": 30,
        "velocidade": 10,
        "xp": 100,
        "gold": 50,
        "descrição": "Um dragão ancião e temível",
    },
    "grifo": {
        "hp": 150,
        "mp": 30,
        "forca": 20,
        "defesa": 15,
        "magia": 15,
        "velocidade": 20,
        "xp": 80,
        "gold": 40,
        "descrição": "Uma criatura mítica metade águia, metade leão",
    },
    "golem": {
        "hp": 180,
        "mp": 0,
        "forca": 22,
        "defesa": 25,
        "magia": 0,
        "velocidade": 4,
        "xp": 90,
        "gold": 45,
        "descrição": "Uma criatura de pedra animada por magia",
    },
    "esqueleto": {
        "hp": 70,
        "mp": 25,
        "forca": 10,
        "defesa": 8,
        "magia": 15,
        "velocidade": 8,
        "xp": 25,
        "gold": 20,
        "descrição": "Um esqueleto reanimado por magia negra",
    },
    "fantasma": {
        "hp": 90,
        "mp": 40,
        "forca": 8,
        "defesa": 6,
        "magia": 25,
        "velocidade": 9,
        "xp": 35,
        "gold": 25,
        "descrição": "Um espírito vingativo e mágico",
    },
    "demônio": {
        "hp": 250,
        "mp": 60,
        "forca": 30,
        "defesa": 25,
        "magia": 40,
        "velocidade": 15,
        "xp": 150,
        "gold": 75,
        "descrição": "Um demônio poderoso do submundo",
    },
}

# Itens disponíveis
ITEMS = {
    # Consumíveis
    "poção de vida": {"tipo": "consumível", "efeito": "hp", "valor": 30, "preço": 10},
    "poção de mana": {"tipo": "consumível", "efeito": "mp", "valor": 20, "preço": 15},
    "poção de vida grande": {
        "tipo": "consumível",
        "efeito": "hp",
        "valor": 100,
        "preço": 50,
    },
    "poção de mana grande": {
        "tipo": "consumível",
        "efeito": "mp",
        "valor": 80,
        "preço": 60,
    },
    # Armas do Guerreiro
    "espada de ferro": {
        "tipo": "arma",
        "dano": 10,
        "preço": 50,
        "classes": ["guerreiro"],
        "descrição": "Uma espada básica de ferro",
        "nivel": 1,
        "max_nivel": 5,
        "custo_upgrade": 100,
        "multiplicador_dano": 1.2,
    },
    "espada de aço": {
        "tipo": "arma",
        "dano": 25,
        "preço": 200,
        "classes": ["guerreiro"],
        "descrição": "Uma espada forjada em aço de alta qualidade",
        "nivel": 1,
        "max_nivel": 5,
        "custo_upgrade": 400,
        "multiplicador_dano": 1.2,
        "raridade": "raro",
    },
    "excalibur": {
        "tipo": "arma",
        "dano": 100,
        "preço": 9999,
        "raridade": "lendário",
        "classes": ["guerreiro"],
        "descrição": "A lendária espada do Rei Artur",
        "nivel": 1,
        "max_nivel": 10,
        "custo_upgrade": 2000,
        "multiplicador_dano": 1.5,
    },
    "mjolnir": {
        "tipo": "arma",
        "dano": 150,
        "preço": 15000,
        "raridade": "lendário",
        "classes": ["guerreiro"],
        "descrição": "O martelo do deus Thor, capaz de controlar trovões",
        "nivel": 1,
        "max_nivel": 10,
        "custo_upgrade": 3000,
        "multiplicador_dano": 1.5,
    },
    # Armas do Mago
    "cajado mágico": {
        "tipo": "arma",
        "dano": 8,
        "preço": 40,
        "classes": ["mago"],
        "descrição": "Um cajado que aumenta o poder mágico",
        "nivel": 1,
        "max_nivel": 5,
        "custo_upgrade": 80,
        "multiplicador_dano": 1.2,
    },
    "cajado do arcanista": {
        "tipo": "arma",
        "dano": 30,
        "preço": 300,
        "classes": ["mago"],
        "descrição": "Um cajado usado por arcanistas poderosos",
        "nivel": 1,
        "max_nivel": 5,
        "custo_upgrade": 600,
        "multiplicador_dano": 1.2,
        "raridade": "raro",
    },
    "cajado de gandalf": {
        "tipo": "arma",
        "dano": 120,
        "preço": 12000,
        "raridade": "lendário",
        "classes": ["mago"],
        "descrição": "O lendário cajado do mago Gandalf, o Cinzento",
        "nivel": 1,
        "max_nivel": 10,
        "custo_upgrade": 2400,
        "multiplicador_dano": 1.5,
    },
    "varinha das varinhas": {
        "tipo": "arma",
        "dano": 180,
        "preço": 18000,
        "raridade": "lendário",
        "classes": ["mago"],
        "descrição": "A varinha mais poderosa já criada, feita com a pena de Fawkes",
        "nivel": 1,
        "max_nivel": 10,
        "custo_upgrade": 3600,
        "multiplicador_dano": 1.5,
    },
    # Armas do Arqueiro
    "arco curto": {
        "tipo": "arma",
        "dano": 7,
        "preço": 35,
        "classes": ["arqueiro"],
        "descrição": "Um arco leve e preciso",
        "nivel": 1,
        "max_nivel": 5,
        "custo_upgrade": 70,
        "multiplicador_dano": 1.2,
    },
    "arco longo": {
        "tipo": "arma",
        "dano": 20,
        "preço": 150,
        "classes": ["arqueiro"],
        "descrição": "Um arco longo com maior alcance e precisão",
        "nivel": 1,
        "max_nivel": 5,
        "custo_upgrade": 300,
        "multiplicador_dano": 1.2,
        "raridade": "raro",
    },
    "arco de legolas": {
        "tipo": "arma",
        "dano": 90,
        "preço": 9000,
        "raridade": "lendário",
        "classes": ["arqueiro"],
        "descrição": "O lendário arco do príncipe élfico Legolas",
        "nivel": 1,
        "max_nivel": 10,
        "custo_upgrade": 1800,
        "multiplicador_dano": 1.5,
    },
    "arco de apolo": {
        "tipo": "arma",
        "dano": 160,
        "preço": 16000,
        "raridade": "lendário",
        "classes": ["arqueiro"],
        "descrição": "O arco do deus grego Apolo, capaz de nunca errar o alvo",
        "nivel": 1,
        "max_nivel": 10,
        "custo_upgrade": 3200,
        "multiplicador_dano": 1.5,
    },
}


def save_player_data():
    """Salva os dados dos jogadores em um arquivo JSON"""
    with open("players.json", "w") as f:
        json.dump(players_data, f)


def load_player_data():
    """Carrega os dados dos jogadores de um arquivo JSON"""
    global players_data
    if os.path.exists("players.json"):
        with open("players.json", "r") as f:
            players_data = json.load(f)
            
        # Adiciona o atributo dano_bonus aos jogadores existentes
        for player_id, player in players_data.items():
            if "dano_bonus" not in player:
                player["dano_bonus"] = 0
                
        # Salva os dados atualizados
        save_player_data()


def create_player(user_id: str, name: str, class_name: str) -> Dict:
    """Cria um novo jogador"""
    if class_name.lower() not in CLASSES:
        raise ValueError("Classe inválida")

    player = {
        "nome": name,
        "classe": class_name.lower(),
        "nivel": 1,
        "xp": 0,
        "xp_necessario": 100,
        "gold": 0,
        "inventario": [],
        "equipamentos": {"arma": None, "armadura": None},
        "dano_bonus": 0,  # Bônus de dano das armas
        **CLASSES[class_name.lower()].copy(),
    }

    players_data[str(user_id)] = player
    save_player_data()
    return player


def get_player(user_id: str) -> Optional[Dict]:
    """Obtém os dados de um jogador"""
    return players_data.get(str(user_id))


def update_player(user_id: str, player_data: Dict):
    """Atualiza os dados de um jogador"""
    players_data[str(user_id)] = player_data
    save_player_data()


def add_xp(user_id: str, xp: int):
    """Adiciona XP ao jogador e verifica se ele subiu de nível"""
    player = get_player(user_id)
    if not player:
        return

    player["xp"] += xp
    while player["xp"] >= player["xp_necessario"]:
        player["nivel"] += 1
        player["xp"] -= player["xp_necessario"]
        player["xp_necessario"] = int(player["xp_necessario"] * 1.5)

        # Melhora os atributos do jogador
        for attr in ["hp", "mp", "forca", "defesa", "magia", "velocidade"]:
            player[attr] = int(player[attr] * 1.1)

    update_player(user_id, player)


def add_item(user_id: str, item_name: str):
    """Adiciona um item ao inventário do jogador"""
    player = get_player(user_id)
    if not player:
        return

    if item_name.lower() not in ITEMS:
        raise ValueError("Item inválido")

    player["inventario"].append(item_name.lower())
    update_player(user_id, player)


def remove_item(user_id: str, item_name: str):
    """Remove um item do inventário do jogador"""
    player = get_player(user_id)
    if not player:
        return

    if item_name.lower() in player["inventario"]:
        player["inventario"].remove(item_name.lower())
        update_player(user_id, player)


def equip_item(user_id: str, item_name: str):
    """Equipa um item no jogador"""
    player = get_player(user_id)
    if not player:
        return

    if item_name.lower() not in player["inventario"]:
        raise ValueError("Item não encontrado no inventário")

    # Remove o nível do nome do item para buscar no dicionário
    base_item = item_name.split("+")[0].lower()
    item = ITEMS.get(base_item)
    
    if not item:
        raise ValueError("Item não encontrado no dicionário de itens")

    # Remove os bônus do item atual equipado
    if player["equipamentos"]["arma"]:
        old_item = ITEMS.get(player["equipamentos"]["arma"].split("+")[0].lower())
        if old_item and old_item["tipo"] == "arma":
            # Calcula o dano do item antigo baseado no nível
            old_level = 1
            if "+" in player["equipamentos"]["arma"]:
                try:
                    old_level = int(player["equipamentos"]["arma"].split("+")[1])
                except ValueError:
                    old_level = 1
            old_dano = int(old_item["dano"] * (old_item["multiplicador_dano"] ** (old_level - 1)))
            player["dano_bonus"] = max(0, player["dano_bonus"] - old_dano)

    # Aplica os bônus do novo item
    if item["tipo"] == "arma":
        player["equipamentos"]["arma"] = item_name.lower()
        # Calcula o dano baseado no nível do item
        current_level = 1
        if "+" in item_name:
            try:
                current_level = int(item_name.split("+")[1])
            except ValueError:
                current_level = 1
        player["dano_bonus"] = int(item["dano"] * (item["multiplicador_dano"] ** (current_level - 1)))
    elif item["tipo"] == "armadura":
        player["equipamentos"]["armadura"] = item_name.lower()
        player["defesa"] += item.get("defesa", 0)

    update_player(user_id, player)


def use_item(user_id: str, item_name: str) -> tuple[bool, str]:
    """
    Usa um item consumível do inventário
    Retorna: (sucesso, mensagem)
    """
    player = get_player(user_id)
    if not player:
        return False, "Jogador não encontrado"

    if item_name.lower() not in player["inventario"]:
        return False, "Item não encontrado no inventário"

    item = ITEMS[item_name.lower()]
    if item["tipo"] != "consumível":
        return False, "Este item não é consumível"

    # Aplica o efeito do item
    if item["efeito"] == "hp":
        player["hp"] = min(
            player["hp"] + item["valor"], CLASSES[player["classe"]]["hp"]
        )
        mensagem = f"Recuperou {item['valor']} HP"
    elif item["efeito"] == "mp":
        player["mp"] = min(
            player["mp"] + item["valor"], CLASSES[player["classe"]]["mp"]
        )
        mensagem = f"Recuperou {item['valor']} MP"

    # Remove o item do inventário
    remove_item(user_id, item_name)
    update_player(user_id, player)

    return True, mensagem


def modify_player_attribute(
    user_id: str, attribute: str, value: int
) -> tuple[bool, str]:
    """
    Modifica um atributo do jogador
    Retorna: (sucesso, mensagem)
    """
    player = get_player(user_id)
    if not player:
        return False, "Jogador não encontrado"

    # Lista de atributos que podem ser modificados
    allowed_attributes = [
        "hp",
        "mp",
        "forca",
        "defesa",
        "magia",
        "velocidade",
        "gold",
        "xp",
        "nivel",
    ]

    if attribute.lower() not in allowed_attributes:
        return (
            False,
            f"Atributo inválido. Atributos permitidos: {', '.join(allowed_attributes)}",
        )

    # Verifica limites para atributos específicos
    if attribute.lower() in ["hp", "mp"]:
        max_value = CLASSES[player["classe"]][attribute.lower()]
        if value > max_value:
            value = max_value
        elif value < 0:
            value = 0

    # Aplica a modificação
    player[attribute.lower()] = value
    update_player(user_id, player)

    return True, f"Atributo {attribute} modificado para {value}"


def can_use_item(player_class: str, item_name: str) -> bool:
    """Verifica se o jogador pode usar o item baseado em sua classe"""
    # Normaliza o nome do item para comparação
    item_name = item_name.lower().strip()
    item = ITEMS.get(item_name)

    if not item:
        print(f"Item não encontrado: {item_name}")
        return False

    if item["tipo"] != "arma":
        return True

    # Normaliza os nomes das classes para comparação
    player_class = player_class.lower().strip()
    item_classes = [c.lower().strip() for c in item.get("classes", [])]

    # Debug para verificar as classes
    print(f"Player class: '{player_class}'")
    print(f"Item classes: {item_classes}")
    print(f"Item type: {item['tipo']}")
    print(f"Item name: {item_name}")
    print(f"Item data: {item}")

    # Verifica se a classe do jogador está na lista de classes permitidas
    for allowed_class in item_classes:
        if player_class == allowed_class:
            print(f"Match found: {player_class} == {allowed_class}")
            return True

    print(f"No match found for {player_class}")
    return False


def upgrade_weapon(user_id: str, item_name: str) -> tuple[bool, str]:
    """
    Tenta fazer upgrade de uma arma
    Retorna: (sucesso, mensagem)
    """
    player = get_player(user_id)
    if not player:
        return False, "Jogador não encontrado"

    if item_name.lower() not in player["inventario"]:
        return False, "Item não encontrado no inventário"

    # Remove o nível do nome do item para buscar no dicionário
    base_item = item_name.split("+")[0].lower()
    item = ITEMS.get(base_item)
    
    if not item:
        return False, "Item não encontrado no dicionário de itens"

    if item["tipo"] != "arma":
        return False, "Este item não é uma arma"

    # Obtém o nível atual da arma
    current_level = 1
    if "+" in item_name:
        try:
            current_level = int(item_name.split("+")[1])
        except ValueError:
            return False, "Nível da arma inválido"

    # Verifica se a arma já está no nível máximo
    if current_level >= item["max_nivel"]:
        return False, f"Esta arma já está no nível máximo ({item['max_nivel']})"

    # Calcula o custo do upgrade
    custo_upgrade = item["custo_upgrade"] * current_level

    # Verifica se o jogador tem gold suficiente
    if player["gold"] < custo_upgrade:
        return False, f"Você não tem gold suficiente! Custo: {custo_upgrade} gold"

    # Faz o upgrade
    player["gold"] -= custo_upgrade
    new_level = current_level + 1
    new_dano = int(item["dano"] * (item["multiplicador_dano"] ** (new_level - 1)))

    # Atualiza o item no inventário
    for i, inv_item in enumerate(player["inventario"]):
        if inv_item.lower() == item_name.lower():
            player["inventario"][i] = f"{base_item}+{new_level}"
            break

    update_player(user_id, player)

    return True, f"Arma melhorada para nível {new_level}! Novo dano: {new_dano}"


# Carrega os dados dos jogadores ao iniciar
load_player_data()
