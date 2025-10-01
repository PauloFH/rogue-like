import pygame
import math
import random
from sprites import SpriteSheet
import os
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
    GREEN,
    NPC_HEALTH,
    NPC_SPEED,
    NPC_DAMAGE,
    ITEM_SIZE,
    YELLOW,
)


class Player:
    def __init__(self, x, y):
        self.is_alive = True
        self.spritesheet = SpriteSheet("assets/PlayerSheet.png")
        self.animations = {}
        self.frame_width = 32
        self.frame_height = 32
        self.load_animations()
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
        self.health = PLAYER_MAX_HEALTH
        self.max_health = PLAYER_MAX_HEALTH
        self.speed = PLAYER_SPEED
        self.health_items = 0
        self.ammo_items = 0

    def load_animations(self):
        """Carrega todos os frames para cada animação."""
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
            self.animations[key] = []
            for col in range(frame_count):
                frame = self.spritesheet.get_image(
                    col * self.frame_width,
                    row * self.frame_height,
                    self.frame_width,
                    self.frame_height,
                )
                self.animations[key].append(frame)

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
        if dx == 0 and dy == 0:
            self.state = "idle"
        else:
            self.state = "walking"
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
        world_min_x = 0
        world_min_y = 0
        world_max_x = GRID_SIZE * AREA_WIDTH - self.width
        world_max_y = GRID_SIZE * AREA_HEIGHT - self.height
        self.x = max(world_min_x, min(new_x, world_max_x))
        self.y = max(world_min_y, min(new_y, world_max_y))
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        self.animate()
        if self.health <= 0:
            self.is_alive = False

    def animate(self):
        now = pygame.time.get_ticks()
        anim_key = f"{self.state}_{self.direction}"
        if anim_key != self.current_animation_key:
            self.current_animation_key = anim_key
            self.current_frame = 0

        if anim_key not in self.animations:
            return

        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(
                self.animations[anim_key]
            )
            center = self.rect.center
            self.image = self.animations[anim_key][self.current_frame]
            self.rect = self.image.get_rect(center=center)

    def get_rect(self):
        return self.rect

    def draw(self, screen, viewport):
        if not self.is_alive:
            return
        screen_x, screen_y = viewport.world_to_screen(self.rect.x, self.rect.y)
        screen.blit(self.image, (screen_x, screen_y))
        health_percentage = self.health / self.max_health
        bar_x, bar_y = screen_x, screen_y - 10
        pygame.draw.rect(screen, RED, (bar_x, bar_y, self.rect.width, 5))
        pygame.draw.rect(
            screen, GREEN, (bar_x, bar_y, self.rect.width * health_percentage, 5)
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


class NPC(pygame.sprite.Sprite):
    """Classe base para todos os NPCs."""

    def __init__(self, x, y):
        super().__init__()
        self.x, self.y = float(x), float(y)
        self.is_alive = True
        self.damage_cooldown = 0
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()

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

        self.animate()

    def animate(self):
        """Animação genérica que funciona para subclasses."""
        now = pygame.time.get_ticks()

        anim_sequence = getattr(self, "animation", None)
        if anim_sequence is None:
            anim_sequence = self.animations.get(self.state, [])

        if not anim_sequence:
            return

        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(anim_sequence)
            center = self.rect.center
            self.image = anim_sequence[self.current_frame]
            self.rect = self.image.get_rect(center=center)

    def get_rect(self):
        return self.rect

    def take_damage(self, damage):
        if self.is_alive:
            self.health -= damage
            if self.health <= 0:
                self.health = 0
                self.is_alive = False

    def attack_player(self, player):
        if self.is_alive and self.damage_cooldown <= 0:
            if player.get_rect().colliderect(self.get_rect()):
                player.take_damage(self.damage)
                self.damage_cooldown = 1.0  # Cooldown de 1 segundo
                return True
        return False

    def draw(self, screen, viewport):
        if not self.is_alive:
            return
        screen_x, screen_y = viewport.world_to_screen(self.rect.x, self.rect.y)
        screen.blit(self.image, (screen_x, screen_y))
        if self.health < self.max_health:
            health_percentage = self.health / self.max_health
            bar_x, bar_y = screen_x, screen_y - 7
            pygame.draw.rect(screen, RED, (bar_x, bar_y, self.rect.width, 4))
            pygame.draw.rect(
                screen, GREEN, (bar_x, bar_y, self.rect.width * health_percentage, 4)
            )


class Spider(NPC):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.spritesheet = SpriteSheet("assets/SpiderSheet.png")
        self.frame_width, self.frame_height = 32, 32
        self.animations = {"idle": [], "walking": []}
        self.load_animations()

        self.state = "walking"
        self.image = self.animations["walking"][0]
        self.rect = self.image.get_rect(topleft=(x, y))

        self.health = NPC_HEALTH * 0.8
        self.max_health = self.health
        self.speed = NPC_SPEED * 1.2
        self.damage = NPC_DAMAGE * 0.7
        self.animation_speed = 100

    def load_animations(self):
        for i in range(6):
            self.animations["idle"].append(
                self.spritesheet.get_image(
                    i * self.frame_width, 0, self.frame_width, self.frame_height
                )
            )
        for i in range(6):
            self.animations["walking"].append(
                self.spritesheet.get_image(
                    i * self.frame_width,
                    self.frame_height,
                    self.frame_width,
                    self.frame_height,
                )
            )


class Droid(NPC):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.spritesheet = SpriteSheet("assets/DroidSheet.png")
        self.frame_width, self.frame_height = 32, 32
        self.animation = []
        self.load_animation()

        self.image = self.animation[0]
        self.rect = self.image.get_rect(topleft=(x, y))

        self.health = NPC_HEALTH * 1.5
        self.max_health = self.health
        self.speed = NPC_SPEED * 0.8
        self.damage = NPC_DAMAGE * 1.5
        self.animation_speed = 150

    def load_animation(self):
        for i in range(6):
            self.animation.append(
                self.spritesheet.get_image(
                    i * self.frame_width, 0, self.frame_width, self.frame_height
                )
            )


class Item:
    def __init__(self, x, y, item_type):
        self.item_type = item_type

        if self.item_type == "health":
            image_path = "assets/health.png"
            if os.path.exists(image_path):
                original_image = pygame.image.load(image_path).convert_alpha()
                original_size = original_image.get_size()
                new_size = (int(original_size[0] * 0.5), int(original_size[1] * 0.5))
                self.image = pygame.transform.scale(original_image, new_size)
            else:
                print(
                    f"Aviso: Imagem '{image_path}' não encontrada. Usando cor de fallback."
                )
                self.image = pygame.Surface((16, 16))
                self.image.fill(GREEN)

        elif self.item_type == "ammo":
            image_path = "assets/ammunition.png"
            if os.path.exists(image_path):
                spritesheet = SpriteSheet(image_path)
                ammo_frames = []
                for i in range(3):
                    frame = spritesheet.get_image(i * 16, 0, 16, 16)
                    ammo_frames.append(frame)
                self.image = random.choice(ammo_frames)
            else:
                print(
                    f"Aviso: Imagem '{image_path}' não encontrada. Usando cor de fallback."
                )
                self.image = pygame.Surface((16, 16))
                self.image.fill(YELLOW)
        else:
            self.image = pygame.Surface((16, 16))
            self.image.fill((128, 128, 128))

        self.rect = self.image.get_rect(topleft=(x, y))
        self.collected = False

    def get_rect(self):
        return self.rect

    def draw(self, screen, viewport):
        if self.collected:
            return
        screen_x, screen_y = viewport.world_to_screen(self.rect.x, self.rect.y)
        screen.blit(self.image, (screen_x, screen_y))
