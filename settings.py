"""
Arquivo de Configurações Globais

Este arquivo centraliza todas as constantes e parâmetros ajustáveis do jogo.
Facilita o balanceamento e a modificação de características do jogo sem
precisar alterar a lógica principal.
"""

# ----------------------------------------------------------------------------
# TELA E GERAL
# ----------------------------------------------------------------------------
SCREEN_WIDTH = 1024  # Largura inicial da janela
SCREEN_HEIGHT = 768  # Altura inicial da janela
FPS = 60  # Frames por segundo, controla a velocidade geral do jogo

# ----------------------------------------------------------------------------
# OBJETIVO E REGRAS DO JOGO
# REQUISITO: "Sobreviver durante um determinado tempo"
# ----------------------------------------------------------------------------
GAME_DURATION = 300  # Duração da partida em segundos (5 minutos)

# ----------------------------------------------------------------------------
# MUNDO E ÁREAS
# REQUISITOS:
# - "Implementar um nível de jogo contendo 9 áreas organizadas em uma malha"
# - "Nem todas as áreas estarão ativas"
# - "Haverão, no máximo, 4 áreas ativas"
# - "Uma área vizinha à atual só ficará ativa quando o personagem chegar 'próximo' a sua borda"
# - "Teste o balanceamento em diferentes cenários: Áreas pequenas/médias/grandes"
# ----------------------------------------------------------------------------
GRID_SIZE = 3  # Tamanho da malha (3x3 = 9 áreas)
AREA_WIDTH = 800  # Largura de cada área (em pixels)
AREA_HEIGHT = 600  # Altura de cada área (em pixels)

# Distância do centro de uma área para o jogador que a ativa.
# Este valor, combinado com a lógica em `WorldGrid.update_active_areas`,
# define a proximidade necessária para ativar uma área.
AREA_ACTIVATION_DISTANCE = 500

# Limita o número de áreas que podem estar ativas simultaneamente.
MAX_ACTIVE_AREAS = 4

# ----------------------------------------------------------------------------
# JOGADOR
# REQUISITOS:
# - "O jogador pode coletar itens de saúde (➕) e munição (⚡)"
# - "Qualquer personagem (NPC ou jogador) com saúde não positiva, morre"
# ----------------------------------------------------------------------------
PLAYER_SIZE = 32  # Tamanho do sprite do jogador
PLAYER_SPEED = 200  # Velocidade de movimento do jogador (pixels por segundo)
PLAYER_MAX_HEALTH = 100  # Saúde máxima do jogador

# ----------------------------------------------------------------------------
# INIMIGOS (NPCs)
# REQUISITOS:
# - "inimigos (NPCs)"
# - "Apenas os NPCs das áreas ativas serão atualizados"
# - "Ir em direção ao jogador"
# - "Enquanto houver sobreposição com o jogador, haverá danos à saúde do jogador"
# - "Teste o balanceamento em diferentes cenários: Dezenas/centenas/milhares de inimigos"
# ----------------------------------------------------------------------------
NPC_SIZE = 24  # Tamanho do sprite do NPC
NPC_SPEED = 50  # Velocidade base de movimento dos NPCs
NPC_DAMAGE = 10  # Dano base causado pelos NPCs por segundo
NPC_HEALTH = 50  # Saúde base dos NPCs

# ----------------------------------------------------------------------------
# ITENS COLETÁVEIS
# REQUISITOS:
# - "caixas de primeiros socorros"
# - "caixas de munição"
# - "Ao usar ➕, a saúde do jogador é recuperada"
# - "Ao usar ⚡, os inimigos ao redor sofrem danos"
# ----------------------------------------------------------------------------
ITEM_SIZE = 16  # Tamanho dos sprites dos itens
HEALTH_RESTORE = 25  # Quantidade de saúde restaurada por um item de vida
AMMO_DAMAGE = 30  # Dano causado a NPCs pelo item de munição
AMMO_RADIUS = 64  # Raio de efeito do item de munição (em pixels)

# ----------------------------------------------------------------------------
# CORES (para UI e debug)
# ----------------------------------------------------------------------------
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
