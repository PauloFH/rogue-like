"""
Gerenciamento do Mundo e das Áreas

Este arquivo define a estrutura do mundo do jogo, que é dividido em uma malha (grid)
de áreas. Ele controla quais áreas estão ativas e o que acontece dentro delas.

REQUISITOS ATENDIDOS:
- Implementação de um nível com 9 áreas em uma malha (WorldGrid).
- Geração de estado inicial aleatório (Area.load).
- Ativação de áreas vizinhas com base na proximidade (WorldGrid.update_active_areas).
- Limite de, no máximo, 4 áreas ativas (WorldGrid.update_active_areas).
- Atualização apenas de NPCs em áreas ativas (Area.update).
- Carregamento/liberação dinâmica de áreas (Area.load/unload).
"""
import pygame
import math
import random
from settings import (
    AREA_WIDTH,
    AREA_HEIGHT,
    GRID_SIZE,
    MAX_ACTIVE_AREAS,
    GRID_SIZE,
    AREA_ACTIVATION_DISTANCE,
    GREEN,
    GRAY,
    ITEM_SIZE,
    NPC_SIZE,
)
from entities import Spider, Droid, Item
from sprites import SpriteSheet


class Area:
    """
    Representa uma única área (célula) na malha do mundo.

    Cada área contém seus próprios NPCs, itens e elementos de cenário.
    Ela pode ser carregada (em memória) e ativada (lógica em execução)
    dinamicamente para otimizar o desempenho.
    """
    def __init__(self, grid_x, grid_y):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.world_x = grid_x * AREA_WIDTH
        self.world_y = grid_y * AREA_HEIGHT
        self.ground_tiles = []
        self.decorations = []
        self.tile_map = []
        self.tile_size = 16
        self.is_active = False
        self.is_loaded = False
        self.npcs = []
        self.items = []

    def load(self):
        """
        Carrega os dados da área, gerando NPCs e itens aleatoriamente.
        Este método cumpre o requisito de "gerado aleatoriamente".
        O bônus de "carregadas / liberadas dinamicamente" é implementado aqui.
        """
        if self.is_loaded:
            return
        try:
            ground_spritesheet = SpriteSheet("assets/ground_tileset.png")
            for row in range(3):
                for col in range(3):
                    tile = ground_spritesheet.get_image(
                        col * self.tile_size,
                        row * self.tile_size,
                        self.tile_size,
                        self.tile_size,
                    )
                    self.ground_tiles.append(tile)

            for y in range(0, AREA_HEIGHT, self.tile_size):
                for x in range(0, AREA_WIDTH, self.tile_size):
                    chosen_tile = random.choice(self.ground_tiles)
                    self.tile_map.append((chosen_tile, (x, y)))

        except (pygame.error, FileNotFoundError):
            print(
                "Aviso: 'assets/ground_tileset.png' não encontrado. O chão não será desenhado."
            )
            self.ground_tiles = None

        try:
            all_marks = []

            marks_16_sheet = SpriteSheet("assets/marks_16.png")
            for row in range(5):
                for col in range(14):
                    all_marks.append(
                        marks_16_sheet.get_image(col * 16, row * 16, 16, 16)
                    )
            marks_48_sheet = SpriteSheet("assets/marks_48.png")
            for i in range(3):
                all_marks.append(marks_48_sheet.get_image(i * 48, 0, 48, 48))
            for _ in range(random.randint(10, 25)):
                mark_image = random.choice(all_marks)
                pos_x = self.world_x + random.randint(
                    0, AREA_WIDTH - mark_image.get_width()
                )
                pos_y = self.world_y + random.randint(
                    0, AREA_HEIGHT - mark_image.get_height()
                )
                self.decorations.append((mark_image, (pos_x, pos_y)))

        except (pygame.error, FileNotFoundError):
            print("Aviso: Não foi possível carregar os spritesheets de 'marks'.")

        # REQUISITO: "inimigos (NPCs)"
        # Gera NPCs em posições aleatórias dentro da área.
        for _ in range(random.randint(5, 15)):
            x = self.world_x + random.randint(50, AREA_WIDTH - 50)
            y = self.world_y + random.randint(50, AREA_HEIGHT - 50)

            if random.random() < 0.7:
                self.npcs.append(Spider(x, y, self))
            else:
                self.npcs.append(Droid(x, y, self))

        # REQUISITOS: "caixas de primeiros socorros" e "caixas de munição"
        # Gera itens de vida.
        for _ in range(random.randint(2, 5)):
            x = self.world_x + random.randint(25, AREA_WIDTH - 25)
            y = self.world_y + random.randint(25, AREA_HEIGHT - 25)
            self.items.append(Item(x, y, "health"))

        # Gera itens de munição.
        for _ in range(random.randint(1, 3)):
            x = self.world_x + random.randint(25, AREA_WIDTH - 25)
            y = self.world_y + random.randint(25, AREA_HEIGHT - 25)
            self.items.append(Item(x, y, "ammo"))

        self.is_loaded = True

    def get_distance_to_player(self, player_x, player_y):
        """Calcula a distância do centro desta área até a posição do jogador."""
        center_x = self.world_x + AREA_WIDTH // 2
        center_y = self.world_y + AREA_HEIGHT // 2
        return math.sqrt((player_x - center_x) ** 2 + (player_y - center_y) ** 2)

    def unload(self):
        """
        Libera os recursos da área da memória.
        Parte do requisito bônus de gerenciamento dinâmico de memória.
        """
        self.npcs.clear()
        self.items.clear()
        self.is_loaded = False

    def activate(self):
        """Ativa a área, carregando-a se necessário."""
        if not self.is_loaded:
            self.load()
        self.is_active = True

    def deactivate(self):
        """Desativa a área."""
        self.is_active = False

    def update(self, dt, player):
        """
        Atualiza a lógica dos NPCs na área.
        REQUISITO: "Apenas os NPCs das áreas ativas serão atualizados"
        Este método só é chamado pela WorldGrid para áreas ativas.
        """
        if not self.is_active:
            return
        for npc in self.npcs:
            npc.update(dt, player)

    def draw(self, surface, viewport):
        """Desenha o conteúdo da área se estiver visível na viewport."""
        if not self.is_loaded:
            return

        if self.ground_tiles:
            for tile_image, (local_x, local_y) in self.tile_map:
                world_x = self.world_x + local_x
                world_y = self.world_y + local_y
                if viewport.is_visible(
                    world_x, world_y, self.tile_size, self.tile_size
                ):
                    screen_x, screen_y = viewport.world_to_screen(world_x, world_y)
                    surface.blit(tile_image, (screen_x, screen_y))

        for image, (world_x, world_y) in self.decorations:
            if viewport.is_visible(
                world_x, world_y, image.get_width(), image.get_height()
            ):
                screen_pos = viewport.world_to_screen(world_x, world_y)
                surface.blit(image, screen_pos)

        # Desenha os itens
        for item in self.items:
            if viewport.is_visible(
                item.rect.x, item.rect.y, item.rect.width, item.rect.height
            ):
                # CORRIGIDO AQUI (ao passar o parâmetro)
                item.draw(surface, viewport)

        # Desenha os NPCs
        for npc in self.npcs:
            # A verificação de visibilidade aqui estava inconsistente, corrigido também
            if viewport.is_visible(
                npc.rect.x, npc.rect.y, npc.rect.width, npc.rect.height
            ):
                # CORRIGIDO AQUI (ao passar o parâmetro)
                npc.draw(surface, viewport)

        def get_distance_to_player(self, player_x, player_y):
            center_x = self.world_x + AREA_WIDTH // 2
            center_y = self.world_y + AREA_HEIGHT // 2
            return math.sqrt((player_x - center_x) ** 2 + (player_y - center_y) ** 2)


class WorldGrid:
    """
    Gerencia a coleção de todas as áreas do jogo, formando a malha 3x3.

    REQUISITO: "Implementar um nível de jogo contendo 9 áreas organizadas em uma malha"
    Esta classe cria e armazena as 9 áreas em um dicionário.
    """
    def __init__(self):
        self.areas = {}
        self.active_areas = set()
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                self.areas[(x, y)] = Area(x, y)

    def update_active_areas(self, player_x, player_y):
        """
        Determina quais áreas devem estar ativas com base na proximidade do jogador.

        REQUISITOS:
        - "Uma área vizinha à atual só ficará ativa quando o personagem chegar 'próximo' a sua borda"
        - "Haverão, no máximo, 4 áreas ativas"
        - BÔNUS: "Ter as áreas carregadas / liberadas dinamicamente da memória"
        """
        new_active_areas = set()
        distances = []
        # 1. Calcula a distância de todas as áreas para o jogador.
        for coord, area in self.areas.items():
            distance = area.get_distance_to_player(player_x, player_y)
            distances.append((distance, coord, area))

        # 2. Ordena as áreas pela distância e seleciona as candidatas a ativas.
        distances.sort()
        for i, (distance, coord, area) in enumerate(distances):
            if i < MAX_ACTIVE_AREAS and distance < AREA_ACTIVATION_DISTANCE * 2:
                new_active_areas.add(coord)

        # 3. Desativa e descarrega áreas que não estão mais no conjunto ativo.
        for coord in self.active_areas - new_active_areas:
            self.areas[coord].deactivate()
            self.areas[coord].unload()

        # 4. Ativa (e carrega, se necessário) novas áreas.
        for coord in new_active_areas - self.active_areas:
            self.areas[coord].activate()

        self.active_areas = new_active_areas

    def update(self, dt, player):
        """Atualiza apenas as áreas ativas."""
        for coord in self.active_areas:
            self.areas[coord].update(dt, player)

    def draw(self, surface, viewport):
        """Desenha todas as áreas (visíveis)."""
        # A própria área/entidade decide se deve ser desenhada com base na viewport.
        for area in self.areas.values():
            area.draw(surface, viewport)

    def get_active_entities(self):
        """
        Retorna uma lista de todos os NPCs e itens contidos APENAS nas áreas ativas.
        Usado para colisões e interações globais.
        """
        npcs = []
        items = []
        for coord in self.active_areas:
            area = self.areas[coord]
            npcs.extend(area.npcs)
            items.extend(area.items)
        return npcs, items
