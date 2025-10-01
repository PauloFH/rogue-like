import pygame
import sys
import time
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    AREA_WIDTH,
    AREA_HEIGHT,
    GAME_DURATION,
    FPS,
    BLACK,
    WHITE,
    GREEN,
    RED,
    YELLOW,
    AMMO_RADIUS,
)
from camera import Viewport
from world import WorldGrid
from entities import Player


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Jogo de Sobrevivência Modular")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.running = True
        self.game_start_time = time.time()
        self.ammo_effect = None

        self.viewport = Viewport()
        self.world_grid = WorldGrid()
        self.player = Player(AREA_WIDTH // 2, AREA_HEIGHT // 2)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_h:
                    self.player.use_health_item()
                elif event.key == pygame.K_SPACE:
                    npcs, _ = self.world_grid.get_active_entities()
                    if self.player.use_ammo_item(npcs):
                        player_center_x = self.player.rect.centerx
                        player_center_y = self.player.rect.centery
                        self.ammo_effect = {
                            "pos": (player_center_x, player_center_y),
                            "timer": 0.2,
                        }

    def check_collisions(self):
        if not self.player.is_alive:
            return

        npcs, items = self.world_grid.get_active_entities()
        player_rect = self.player.get_rect()

        for npc in npcs:
            if npc.is_alive:
                npc.attack_player(self.player)

        for item in items:
            if not item.collected and player_rect.colliderect(item.get_rect()):
                item.collected = True
                if item.item_type == "health":
                    self.player.health_items += 1
                elif item.item_type == "ammo":
                    self.player.ammo_items += 1

    def update(self, dt):
        if not self.player.is_alive or self.is_game_won():
            return

        if self.ammo_effect:
            self.ammo_effect["timer"] -= dt
            if self.ammo_effect["timer"] <= 0:
                self.ammo_effect = None

        keys = pygame.key.get_pressed()
        self.player.update(dt, keys)
        self.viewport.update(
            self.player.rect.centerx,
            self.player.rect.centery,
        )
        self.world_grid.update_active_areas(self.player.x, self.player.y)
        self.world_grid.update(dt, (self.player.x, self.player.y))
        self.check_collisions()

    def draw(self):
        self.screen.fill(BLACK)
        self.world_grid.draw(self.screen, self.viewport)
        self.player.draw(self.screen, self.viewport)
        self.draw_ammo_effect()

        self.draw_ui()
        pygame.display.flip()

    def draw_ammo_effect(self):
        if self.ammo_effect:

            effect_pos_world = self.ammo_effect["pos"]
            effect_pos_screen = self.viewport.world_to_screen(
                effect_pos_world[0], effect_pos_world[1]
            )

            surface = pygame.Surface(
                (AMMO_RADIUS * 2, AMMO_RADIUS * 2), pygame.SRCALPHA
            )

            alpha = int(
                150 * (self.ammo_effect["timer"] / 0.2)
            )  # 150 é a opacidade inicial
            pygame.draw.circle(
                surface, (*YELLOW, alpha), (AMMO_RADIUS, AMMO_RADIUS), AMMO_RADIUS
            )

            self.screen.blit(
                surface,
                (
                    effect_pos_screen[0] - AMMO_RADIUS,
                    effect_pos_screen[1] - AMMO_RADIUS,
                ),
            )

    def draw_ui(self):
        elapsed_time = time.time() - self.game_start_time
        remaining_time = max(0, GAME_DURATION - elapsed_time)

        texts = [
            f"Tempo: {remaining_time:.1f}s",
            f"Vida: {self.player.health}/{self.player.max_health}",
            f"Itens: ♥{self.player.health_items} ⚡{self.player.ammo_items}",
        ]

        for i, text in enumerate(texts):
            surface = self.font.render(text, True, WHITE)
            self.screen.blit(surface, (10, 10 + i * 30))

        if self.is_game_won():
            self.draw_end_screen("VOCÊ VENCEU! Sobreviveu por 5 minutos!", GREEN)
        elif not self.player.is_alive:
            self.draw_end_screen("GAME OVER! Pressione ESC para sair", RED)

    def draw_end_screen(self, text, color):
        font = pygame.font.Font(None, 48)
        surface = font.render(text, True, color)
        text_rect = surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(surface, text_rect)

    def is_game_won(self):
        return (time.time() - self.game_start_time) >= GAME_DURATION

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
