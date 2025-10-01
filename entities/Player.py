import math
import pygame
from sprites import SpriteSheet
from settings import (
    PLAYER_MAX_HEALTH,
    PLAYER_SPEED,
    HEALTH_RESTORE,
    AMMO_RADIUS,
    AMMO_DAMAGE,
    RED,
    GRID_SIZE,
    AREA_WIDTH,
    AREA_HEIGHT,
    GREEN
)

class Player:
    def __init__(self, x, y):
        self.is_alive = True
        self.spritesheet = SpriteSheet("assets/PlayerSheet.png")
        self.animations = {}
        self.frame_width = self.frame_height = 32
        self._load_animations()
        self.state = "idle"
        self.direction = "front"
        self.current_animation_key = "idle_front"
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = 120
        self.image = self.animations[self.current_animation_key][0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.x, self.y = float(self.rect.x), float(self.rect.y)
        self.width, self.height = self.rect.size
        self.health = self.max_health = PLAYER_MAX_HEALTH
        self.speed = PLAYER_SPEED
        self.health_items = 0
        self.ammo_items = 0

    def _load_animations(self):
        anim_map = {
            0: ("idle", "front", 5),
            1: ("idle", "back", 5),
            2: ("idle", "right", 5),
            3: ("idle", "left", 5),
            4: ("walking", "front", 6),
            5: ("walking", "back", 6),
            6: ("walking", "right", 6),
            7: ("walking", "left", 6),
        }
        for row, (state, direction, frame_count) in anim_map.items():
            key = f"{state}_{direction}"
            self.animations[key] = [
                self.spritesheet.get_image(
                    col * self.frame_width,
                    row * self.frame_height,
                    self.frame_width,
                    self.frame_height,
                )
                for col in range(frame_count)
            ]

    def _animate(self):
        now = pygame.time.get_ticks()
        anim_key = f"{self.state}_{self.direction}"
        if anim_key != self.current_animation_key:
            self.current_animation_key = anim_key
            self.current_frame = 0
        sequence = self.animations.get(anim_key)
        if sequence and now - self.last_update > self.animation_speed:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(sequence)
            center = self.rect.center
            self.image = sequence[self.current_frame]
            self.rect = self.image.get_rect(center=center)

    def update(self, dt, keys):
        if not self.is_alive:
            return
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed * dt
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= self.speed * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += self.speed * dt
        self.state = "idle" if dx == 0 and dy == 0 else "walking"
        if dx > 0:
            self.direction = "right"
        elif dx < 0:
            self.direction = "left"
        elif dy > 0:
            self.direction = "front"
        elif dy < 0:
            self.direction = "back"
        new_x = self.x + dx
        new_y = self.y + dy
        wmin_x = 0
        wmin_y = 0
        wmax_x = GRID_SIZE * AREA_WIDTH - self.width
        wmax_y = GRID_SIZE * AREA_HEIGHT - self.height
        self.x = max(wmin_x, min(new_x, wmax_x))
        self.y = max(wmin_y, min(new_y, wmax_y))
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        self._animate()
        if self.health <= 0:
            self.is_alive = False

    def take_damage(self, dmg):
        if self.is_alive:
            self.health = max(0, self.health - dmg)

    def use_health_item(self):
        if self.health_items and self.health < self.max_health:
            self.health_items -= 1
            self.health = min(self.max_health, self.health + HEALTH_RESTORE)
            return True
        return False

    def use_ammo_item(self, npcs):
        if not self.ammo_items:
            return 0
        self.ammo_items -= 1
        hit = 0
        for npc in npcs:
            dist = math.hypot(
                self.rect.centerx - npc.rect.centerx,
                self.rect.centery - npc.rect.centery,
            )
            if dist <= AMMO_RADIUS:
                npc.take_damage(AMMO_DAMAGE)
                hit += 1
        return hit

    def draw(self, surface, viewport):
        if not self.is_alive:
            return
        sx, sy = viewport.world_to_screen(self.rect.x, self.rect.y)
        surface.blit(self.image, (sx, sy))
        pct = self.health / self.max_health
        bar_x, bar_y = sx, sy - 10
        pygame.draw.rect(surface, RED, (bar_x, bar_y, self.rect.width, 5))
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, self.rect.width * pct, 5))

    def get_rect(self):
        return self.rect