import pygame

from entities.Npc.NPC import NPC
from sprites import SpriteSheet
from settings import (
    NPC_HEALTH,
    NPC_SPEED,
    NPC_DAMAGE,
)

class Spider(NPC):
    def __init__(self, x, y, area):
        super().__init__(x, y, area)
        self.spritesheet = SpriteSheet("assets/SpiderSheet.png")
        self.frame_width = self.frame_height = 32
        self.animations = {"idle": [], "walking": []}
        self._load_animations()
        self.state = "walking"
        self.image = self.animations["walking"][0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.health = self.max_health = NPC_HEALTH * 0.8
        self.speed = NPC_SPEED * 1.2
        self.damage = NPC_DAMAGE * 0.7
        self.animation_speed = 100
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()

    def _load_animations(self):
        for i in range(6):
            self.animations["idle"].append(
                self.spritesheet.get_image(i * self.frame_width, 0, self.frame_width, self.frame_height)
            )
        for i in range(6):
            self.animations["walking"].append(
                self.spritesheet.get_image(i * self.frame_width, self.frame_height, self.frame_width, self.frame_height)
            )

    def _animate(self):
        now = pygame.time.get_ticks()
        seq = self.animations[self.state]
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(seq)
            center = self.rect.center
            self.image = seq[self.current_frame]
            self.rect = self.image.get_rect(center=center)
