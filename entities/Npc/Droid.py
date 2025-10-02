import pygame

from entities.Npc.NPC import NPC
from sprites import SpriteSheet
from settings import (
    NPC_HEALTH,
    NPC_SPEED,
    NPC_DAMAGE,

)
class Droid(NPC):
    def __init__(self, x, y, area):
        super().__init__(x, y, area)
        self.spritesheet = SpriteSheet("assets/DroidSheet.png")
        self.frame_width = self.frame_height = 32
        self.animation = []
        self._load_animation()
        self.image = self.animation[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.health = self.max_health = NPC_HEALTH * 1.5
        self.speed = NPC_SPEED * 0.8
        self.damage = NPC_DAMAGE * 1.5
        self.animation_speed = 150
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()

    def _load_animation(self):
        for i in range(6):
            self.animation.append(
                self.spritesheet.get_image(i * self.frame_width, 0, self.frame_width, self.frame_height)
            )

    def _animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.animation)
            center = self.rect.center
            self.image = self.animation[self.current_frame]
            self.rect = self.image.get_rect(center=center)
