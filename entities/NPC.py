import math
import pygame
from settings import (
    NPC_SIZE,
    RED,
    AREA_WIDTH,
    AREA_HEIGHT,
    GREEN,
)


class NPC:
    def __init__(self, x, y, area, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rect = pygame.Rect(x, y, NPC_SIZE, NPC_SIZE)
        self.is_alive = True
        self.damage_cooldown = 2.0
        self.area = area
        self.area_rect = pygame.Rect(area.world_x, area.world_y, AREA_WIDTH, AREA_HEIGHT)

    def update(self, dt, player):
        if not self.is_alive:
            return
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy) or 1
        self.rect.x += self.speed * dt * dx / dist
        self.rect.y += self.speed * dt * dy / dist
        self.rect.clamp_ip(self.area_rect)
        self._animate()
        if not self.area_rect.collidepoint(player.rect.center):
            return
        if self.damage_cooldown > 0:
            self.damage_cooldown -= dt

    def attack_player(self, player):
        # Dano por contato se houver colisão
        if self.is_alive and self.damage_cooldown <= 0:
            if player.get_rect().colliderect(self.rect):
                player.take_damage(self.damage)
                self.damage_cooldown = 1.0
                return True
        return False

    def draw(self, surface, viewport):
        if not self.is_alive:
            return
        sx, sy = viewport.world_to_screen(self.rect.x, self.rect.y)
        surface.blit(self.image, (sx, sy))
        if self.health < self.max_health:
            pct = self.health / self.max_health
            bar_x, bar_y = sx, sy - 7
            pygame.draw.rect(surface, RED, (bar_x, bar_y, self.rect.width, 4))
            pygame.draw.rect(surface, GREEN, (bar_x, bar_y, self.rect.width * pct, 4))

    def take_damage(self, dmg):
        if self.is_alive:
            self.health -= dmg
            if self.health <= 0:
                self.health = 0
                self.is_alive = False

    def _animate(self):
        pass