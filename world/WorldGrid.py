from settings import (
    GRID_SIZE,
    MAX_ACTIVE_AREAS,
    AREA_ACTIVATION_DISTANCE,
)
from world.Area import Area


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

    def update(self, dt, player):
        for coord in self.active_areas:
            self.areas[coord].update(dt, player)

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
