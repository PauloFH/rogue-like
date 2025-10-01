"""
Definição de todas as entidades do jogo: Jogador, NPCs e Itens.

Este arquivo contém a lógica para o comportamento, atualização e renderização
de cada tipo de entidade.

REQUISITOS ATENDIDOS:
- Implementação de inimigos (NPCs) (classes NPC, Spider, Droid).
- Implementação de caixas de primeiros socorros e munição (classe Item).
- Comportamento de NPC: ir em direção ao jogador (NPC.update).
- Comportamento de NPC: causar dano ao jogador por sobreposição (NPC.attack_player).
- Uso de item de saúde (➕) para recuperar vida (Player.use_health_item).
- Uso de item de munição (⚡) para causar dano em área (Player.use_ammo_item).
- Morte de personagem (jogador ou NPC) com saúde não positiva (Player.update, NPC.take_damage).
"""
import math
import os
import random
import pygame

from sprites import SpriteSheet
from settings import (
    NPC_SIZE,
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
    ITEM_SIZE,  # parece não usado, mas mantive
    YELLOW,
)


# ────────────────────
# PLAYER
# ────────────────────
class Player:
    """
    Representa o personagem controlado pelo usuário.

    Contém a lógica de movimento, saúde, inventário de itens e animações.
    """
    def __init__(self, x, y):
        self.is_alive = True

        # animações
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

        # atributos de jogo
        self.health = self.max_health = PLAYER_MAX_HEALTH
        self.speed = PLAYER_SPEED
        self.health_items = 0
        self.ammo_items = 0

    # ---------- animação ----------
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

    # ---------- lógica ----------
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

        # limites do mundo
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

        # REQUISITO: "Qualquer personagem ... com saúde não positiva, morre"
        if self.health <= 0:
            self.is_alive = False

    # ---------- utilidades ----------
    def take_damage(self, dmg):  # recebido de NPC
        """Reduz a saúde do jogador ao receber dano."""
        if self.is_alive:
            self.health = max(0, self.health - dmg)

    def use_health_item(self):
        """
        REQUISITO: "Ao usar ➕, a saúde do jogador é recuperada"
        Consome um item de vida para restaurar a saúde.
        """
        if self.health_items and self.health < self.max_health:
            self.health_items -= 1
            self.health = min(self.max_health, self.health + HEALTH_RESTORE)
            return True
        return False

    def use_ammo_item(self, npcs):
        """
        REQUISITO: "Ao usar ⚡, os inimigos ao redor sofrem danos"
        Consome um item de munição para causar dano a todos os NPCs em um raio.
        """
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

    # ---------- render ----------
    def draw(self, surface, viewport):
        if not self.is_alive:
            return
        sx, sy = viewport.world_to_screen(self.rect.x, self.rect.y)
        surface.blit(self.image, (sx, sy))

        # barra de vida
        pct = self.health / self.max_health
        bar_x, bar_y = sx, sy - 10
        pygame.draw.rect(surface, RED, (bar_x, bar_y, self.rect.width, 5))
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, self.rect.width * pct, 5))

    def get_rect(self):
        return self.rect


# ────────────────────
# NPC base
# ────────────────────
class NPC:
    """
    Classe base para todos os Inimigos (Non-Player Characters).

    Define o comportamento padrão, como seguir o jogador e atacar.
    """
    def __init__(self, x, y, area, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rect = pygame.Rect(x, y, NPC_SIZE, NPC_SIZE)
        self.is_alive = True
        self.damage_cooldown = 2.0  # segundos
        self.area = area
        self.area_rect = pygame.Rect(
            area.world_x, area.world_y, AREA_WIDTH, AREA_HEIGHT
        )

    def update(self, dt, player):
        """
        REQUISITO: "Ir em direção ao jogador"
        Move o NPC na direção do jogador, mas confinado à sua própria área.
        """
        if not self.is_alive:
            return
        # mover em direção ao player
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy) or 1
        self.rect.x += self.speed * dt * dx / dist
        self.rect.y += self.speed * dt * dy / dist
        self.rect.clamp_ip(self.area_rect) # Garante que o NPC não saia da sua área
        self._animate()
        if not self.area_rect.collidepoint(player.rect.center):
            return
        # cooldown
        if self.damage_cooldown > 0:
            self.damage_cooldown -= dt

    def attack_player(self, player):
        """
        REQUISITO: "Enquanto houver sobreposição com o jogador, haverá danos à saúde do jogador"
        Verifica a colisão e causa dano ao jogador se o cooldown permitir.
        """
        if self.is_alive and self.damage_cooldown <= 0:
            if player.get_rect().colliderect(self.rect):
                player.take_damage(self.damage)
                self.damage_cooldown = 1.0  # 1s
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
        """
        REQUISITO: "Qualquer personagem ... com saúde não positiva, morre"
        Reduz a saúde do NPC e o marca como morto se a saúde chegar a zero.
        """
        if self.is_alive:
            self.health -= dmg
            if self.health <= 0:
                self.health = 0
                self.is_alive = False

    # stub; as subclasses implementam
    def _animate(self):
        pass


# ────────────────────
# SPIDER
# ────────────────────
class Spider(NPC):
    """Uma aranha rápida, mas com menos vida e dano."""
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

    def _animate(self):
        now = pygame.time.get_ticks()
        seq = self.animations[self.state]
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(seq)
            center = self.rect.center
            self.image = seq[self.current_frame]
            self.rect = self.image.get_rect(center=center)


# ────────────────────
# DROID
# ────────────────────
class Droid(NPC):
    """Um droid mais lento, porém mais resistente e com mais dano."""
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
                self.spritesheet.get_image(
                    i * self.frame_width, 0, self.frame_width, self.frame_height
                )
            )

    def _animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.animation)
            center = self.rect.center
            self.image = self.animation[self.current_frame]
            self.rect = self.image.get_rect(center=center)


# ────────────────────
# ITEM
# ────────────────────
class Item:
    """
    Representa um item coletável no mundo (vida ou munição).

    REQUISITOS: "caixas de primeiros socorros", "caixas de munição"
    """
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

    # helpers
    def _load_or_fallback(self, path, color):
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            w, h = img.get_size()
            return pygame.transform.scale(img, (w // 2, h // 2))
        return self._make_fallback_surface(color)

    @staticmethod
    def _make_fallback_surface(color, size=(16, 16)):
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill(color)
        return surf

    # draw
    def draw(self, surface, viewport):
        if self.collected:
            return
        sx, sy = viewport.world_to_screen(self.rect.x, self.rect.y)
        surface.blit(self.image, (sx, sy))

    def get_rect(self):
        return self.rect
