import os
import random
import pygame
from sprites import SpriteSheet
from settings import (
    GREEN,
    YELLOW,
)
class Item:
    def __init__(self, x, y, item_type):
        self.item_type = item_type
        if item_type == "health":
            img_path = "assets/health.png"
            self.image = self._load_or_fallback(img_path, GREEN)
        elif item_type == "ammo":
            img_path = "assets/ammunition.png"
            if os.path.exists(img_path):
                sheet = SpriteSheet(img_path)
                frames = [sheet.get_image(i * 16, 0, 16, 16) for i in range(3)]
                self.image = random.choice(frames)
            else:
                self.image = self._make_fallback_surface(YELLOW)
        else:
            self.image = self._make_fallback_surface((128, 128, 128))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.collected = False

    def _load_or_fallback(self, path, color):
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            w, h = img.get_size()
            return pygame.transform.scale(img, (w, h))
        return self._make_fallback_surface(color)

    @staticmethod
    def _make_fallback_surface(color, size=(16, 16)):
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill(color)
        return surf

    def draw(self, surface, viewport):
        if self.collected:
            return
        sx, sy = viewport.world_to_screen(self.rect.x, self.rect.y)
        surface.blit(self.image, (sx, sy))

    def get_rect(self):
        return self.rect
