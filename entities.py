import pygame
import math
from settings import (
    PLAYER_SIZE,
    PLAYER_MAX_HEALTH,
    PLAYER_SPEED,
    HEALTH_RESTORE,
    AMMO_RADIUS,
    AMMO_DAMAGE,
    BLUE,
    RED,
    GREEN,
    NPC_SIZE,
    NPC_HEALTH,
    NPC_SPEED,
    NPC_DAMAGE,
    ITEM_SIZE,
    YELLOW,
)


class Player:
    def __init__(self, x, y):
        self.is_alive = True
        try:
            self.image = pygame.image.load("assets/player.png").convert_alpha()
        except pygame.error:
            self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
            self.image.fill(BLUE)

        self.rect = self.image.get_rect(topleft=(x, y))

        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.width = self.rect.width
        self.height = self.rect.height

        self.health = PLAYER_MAX_HEALTH
        self.max_health = PLAYER_MAX_HEALTH
        self.speed = PLAYER_SPEED
        self.health_items = 0
        self.ammo_items = 0

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

        self.x += dx
        self.y += dy
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        if self.health <= 0:
            self.is_alive = False

    def use_ammo_item(self, npcs):
        if self.ammo_items > 0:
            self.ammo_items -= 1
            damaged_count = 0
            for npc in npcs:
                distance = math.sqrt(
                    (self.rect.centerx - npc.rect.centerx) ** 2
                    + (self.rect.centery - npc.rect.centery) ** 2
                )
                if distance <= AMMO_RADIUS:
                    npc.take_damage(AMMO_DAMAGE)
                    damaged_count += 1
            return damaged_count > 0
        return False

    def get_rect(self):
        return self.rect

    def draw(self, screen, viewport):
        if not self.is_alive:
            return

        screen_x, screen_y = viewport.world_to_screen(self.rect.x, self.rect.y)
        screen.blit(self.image, (screen_x, screen_y))
        health_percentage = self.health / self.max_health
        bar_x = screen_x
        bar_y = screen_y - 10
        pygame.draw.rect(screen, RED, (bar_x, bar_y, self.width, 5))
        pygame.draw.rect(
            screen, GREEN, (bar_x, bar_y, self.width * health_percentage, 5)
        )

    def take_damage(self, damage):
        if self.is_alive:
            self.health -= damage
            if self.health < 0:
                self.health = 0

    def use_health_item(self):
        if self.health_items > 0 and self.health < self.max_health:
            self.health_items -= 1
            self.health = min(self.max_health, self.health + HEALTH_RESTORE)
            return True
        return False


class NPC:
    def __init__(self, x, y):
        try:
            self.image = pygame.image.load("assets/npc.png").convert_alpha()
        except pygame.error:
            self.image = pygame.Surface((NPC_SIZE, NPC_SIZE))
            self.image.fill(RED)

        self.rect = self.image.get_rect(topleft=(x, y))
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.width = self.rect.width
        self.height = self.rect.height

        self.health = NPC_HEALTH
        self.max_health = NPC_HEALTH
        self.speed = NPC_SPEED
        self.damage = NPC_DAMAGE
        self.is_alive = True
        self.damage_cooldown = 0

    def update(self, dt, player_pos):
        if not self.is_alive:
            return
        player_x, player_y = player_pos[0], player_pos[1]
        dx = player_x - self.rect.centerx
        dy = player_y - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)

        if distance > 0:
            self.x += (dx / distance) * self.speed * dt
            self.y += (dy / distance) * self.speed * dt
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)

        if self.damage_cooldown > 0:
            self.damage_cooldown -= dt

    def get_rect(self):
        return self.rect

    def draw(self, screen, viewport):
        if not self.is_alive:
            return
        screen_x, screen_y = viewport.world_to_screen(self.rect.x, self.rect.y)
        screen.blit(self.image, (screen_x, screen_y))


class Item:
    def __init__(self, x, y, item_type):
        self.item_type = item_type
        image_path = f"assets/{item_type}.png"
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
        except pygame.error:
            self.image = pygame.Surface((ITEM_SIZE, ITEM_SIZE))
            color = GREEN if self.item_type == "health" else YELLOW
            self.image.fill(color)

        self.rect = self.image.get_rect(topleft=(x, y))
        self.collected = False

    def get_rect(self):
        return self.rect

    def draw(self, screen, viewport):
        if self.collected:
            return
        screen_x, screen_y = viewport.world_to_screen(self.rect.x, self.rect.y)
        screen.blit(self.image, (screen_x, screen_y))
