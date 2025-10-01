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

        for _ in range(random.randint(5, 15)):
            x = self.world_x + random.randint(50, AREA_WIDTH - 50)
            y = self.world_y + random.randint(50, AREA_HEIGHT - 50)

            if random.random() < 0.7:
                self.npcs.append(Spider(x, y))
            else:
                self.npcs.append(Droid(x, y))

        for _ in range(random.randint(2, 5)):
            x = self.world_x + random.randint(25, AREA_WIDTH - 25)
            y = self.world_y + random.randint(25, AREA_HEIGHT - 25)
            self.items.append(Item(x, y, "health"))

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
        self.npcs.clear()
        self.items.clear()
        self.is_loaded = False

    def activate(self):
        if not self.is_loaded:
            self.load()
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def update(self, dt, player_pos):
        if not self.is_active:
            return
        for npc in self.npcs:
            npc.update(dt, player_pos)

    def draw(self, surface, viewport):
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
    def __init__(self):
        self.areas = {}
        self.active_areas = set()
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                self.areas[(x, y)] = Area(x, y)

    def update_active_areas(self, player_x, player_y):
        new_active_areas = set()
        distances = []
        for coord, area in self.areas.items():
            distance = area.get_distance_to_player(player_x, player_y)
            distances.append((distance, coord, area))

        distances.sort()
        for i, (distance, coord, area) in enumerate(distances):
            if i < MAX_ACTIVE_AREAS and distance < AREA_ACTIVATION_DISTANCE * 2:
                new_active_areas.add(coord)

        for coord in self.active_areas - new_active_areas:
            self.areas[coord].deactivate()
            self.areas[coord].unload()

        for coord in new_active_areas - self.active_areas:
            self.areas[coord].activate()

        self.active_areas = new_active_areas

    def update(self, dt, player_pos):
        for coord in self.active_areas:
            self.areas[coord].update(dt, player_pos)

    def draw(self, surface, viewport):
        for area in self.areas.values():
            area.draw(surface, viewport)

    def get_active_entities(self):
        npcs = []
        items = []
        for coord in self.active_areas:
            area = self.areas[coord]
            npcs.extend(area.npcs)
            items.extend(area.items)
        return npcs, items
