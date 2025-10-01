import pygame
import math
import random
from settings import (
    AREA_WIDTH,
    AREA_HEIGHT,
    GRID_SIZE,
    MAX_ACTIVE_AREAS,
    AREA_ACTIVATION_DISTANCE,
    GREEN,
    GRAY,
    ITEM_SIZE,
    NPC_SIZE,
)
from entities import NPC, Item


class Area:
    def __init__(self, grid_x, grid_y):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.world_x = grid_x * AREA_WIDTH
        self.world_y = grid_y * AREA_HEIGHT
        self.is_active = False
        self.is_loaded = False
        self.npcs = []
        self.items = []

    def load(self):
        if self.is_loaded:
            return
        for _ in range(random.randint(5, 15)):
            x = self.world_x + random.randint(50, AREA_WIDTH - 50)
            y = self.world_y + random.randint(50, AREA_HEIGHT - 50)
            self.npcs.append(NPC(x, y))

        for _ in range(random.randint(2, 5)):
            x = self.world_x + random.randint(25, AREA_WIDTH - 25)
            y = self.world_y + random.randint(25, AREA_HEIGHT - 25)
            self.items.append(Item(x, y, "health"))

        for _ in range(random.randint(1, 3)):
            x = self.world_x + random.randint(25, AREA_WIDTH - 25)
            y = self.world_y + random.randint(25, AREA_HEIGHT - 25)
            self.items.append(Item(x, y, "ammo"))

        self.is_loaded = True

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

    def draw(self, screen, viewport):
        if not self.is_loaded:
            return

        screen_x, screen_y = viewport.world_to_screen(self.world_x, self.world_y)
        color = GREEN if self.is_active else GRAY
        pygame.draw.rect(
            screen, color, (screen_x, screen_y, AREA_WIDTH, AREA_HEIGHT), 3
        )

        for item in self.items:
            if viewport.is_visible(item.x, item.y, ITEM_SIZE, ITEM_SIZE):
                item.draw(screen, viewport)

        for npc in self.npcs:
            if viewport.is_visible(npc.x, npc.y, NPC_SIZE, NPC_SIZE):
                npc.draw(screen, viewport)

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

    def draw(self, screen, viewport):
        for area in self.areas.values():
            area.draw(screen, viewport)

    def get_active_entities(self):
        npcs = []
        items = []
        for coord in self.active_areas:
            area = self.areas[coord]
            npcs.extend(area.npcs)
            items.extend(area.items)
        return npcs, items
