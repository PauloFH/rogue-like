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
    GRAY,
    GRID_SIZE,
    HEALTH_RESTORE,
)
from camera import Viewport
from world import WorldGrid
from entities import Player


class Game:
    def __init__(self):
        pygame.init()
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height), pygame.RESIZABLE
        )

        pygame.display.set_caption("Jogo de Sobrevivência Modular")
        self.clock = pygame.time.Clock()

        # Fontes para as telas
        self.title_font = pygame.font.Font(None, 74)
        self.instructions_font = pygame.font.Font(None, 36)

        self.running = True

        self.game_state = "start_screen"

        try:
            self.background_tile = pygame.image.load("assets/space.png").convert()
            self.bg_tile_size = self.background_tile.get_size()
        except pygame.error:
            print("Aviso: 'assets/space.png' não encontrada. O fundo será preto.")
            self.background_tile = None

    def reset_game(self):
        """Prepara ou reinicia todas as variáveis para uma nova partida."""
        print("Iniciando novo jogo!")
        self.game_start_time = time.time()
        self.viewport = Viewport(self.screen_width, self.screen_height)
        self.world_grid = WorldGrid()
        self.player = Player(AREA_WIDTH // 2, AREA_HEIGHT // 2)
        # Muda o estado para 'jogando'
        self.game_state = "playing"

    def handle_gameplay_events(self):
        """Lida com os eventos APENAS durante o gameplay."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.handle_resize(event)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_h:
                    self.player.use_health_item()
                elif event.key == pygame.K_SPACE:
                    npcs, _ = self.world_grid.get_active_entities()
                    self.player.use_ammo_item(npcs)

    def handle_menu_events(self):
        """Lida com os eventos nas telas de início e fim."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.handle_resize(event)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if self.game_state == "start_screen" and event.key == pygame.K_RETURN:
                    self.reset_game()
                if (
                    self.game_state in ["game_over", "win_screen"]
                    and event.key == pygame.K_r
                ):
                    self.reset_game()

    def handle_resize(self, event):
        """Lida com o redimensionamento da janela."""
        self.screen_width = event.w
        self.screen_height = event.h
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height), pygame.RESIZABLE
        )
        if hasattr(self, "viewport"):
            self.viewport.update_size(self.screen_width, self.screen_height)

    def update(self, dt):
        if self.game_state != "playing":
            return
        if hasattr(self, "ammo_effect") and self.ammo_effect:
            self.ammo_effect["timer"] -= dt
            if self.ammo_effect["timer"] <= 0:
                self.ammo_effect = None
        if not self.player.is_alive:
            self.game_state = "game_over"
            return
        if time.time() - self.game_start_time >= GAME_DURATION:
            self.game_state = "win_screen"
            return
        keys = pygame.key.get_pressed()
        self.player.update(dt, keys)
        self.viewport.update(self.player.rect.centerx, self.player.rect.centery)
        self.world_grid.update_active_areas(self.player.x, self.player.y)
        self.world_grid.update(dt, (self.player.x, self.player.y))
        self.check_collisions()

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
                    self.player.health = min(
                        self.player.max_health, self.player.health + HEALTH_RESTORE
                    )
                elif item.item_type == "ammo":
                    self.player.ammo_items += 1

    def draw_background(self):
        """Desenha o fundo infinito de espaço se a imagem existir."""
        if not self.background_tile:
            self.screen.fill(BLACK)
            return
        if not hasattr(self, "viewport"):
            return

        offset_x = self.viewport.x % self.bg_tile_size[0]
        offset_y = self.viewport.y % self.bg_tile_size[1]
        for x in range(
            -self.bg_tile_size[0],
            self.screen_width + self.bg_tile_size[0],
            self.bg_tile_size[0],
        ):
            for y in range(
                -self.bg_tile_size[1],
                self.screen_height + self.bg_tile_size[1],
                self.bg_tile_size[1],
            ):
                self.screen.blit(self.background_tile, (x - offset_x, y - offset_y))
    def draw_gameplay(self):
        """Desenha todos os elementos do jogo quando o estado é 'playing'."""
        self.draw_background()
        self.world_grid.draw(self.screen, self.viewport)
        self.player.draw(self.screen, self.viewport)
        self.draw_ammo_effect()
        self.draw_ui()
        self.draw_minimap()

    def draw_ammo_effect(self):
        if hasattr(self, "ammo_effect") and self.ammo_effect:
            effect_pos_world = self.ammo_effect["pos"]
            effect_pos_screen = self.viewport.world_to_screen(
                effect_pos_world[0], effect_pos_world[1]
            )
            surface = pygame.Surface(
                (AMMO_RADIUS * 2, AMMO_RADIUS * 2), pygame.SRCALPHA
            )
            alpha = int(150 * (self.ammo_effect["timer"] / 0.2))
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
            surface = self.instructions_font.render(text, True, WHITE)
            self.screen.blit(surface, (10, 10 + i * 30))

    def draw_start_screen(self):
        """Desenha a tela inicial."""
        self.screen.fill(BLACK)
        title_surf = self.title_font.render("Sobrevivência Modular", True, WHITE)
        inst_surf = self.instructions_font.render(
            "Pressione ENTER para começar", True, GREEN
        )

        title_rect = title_surf.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 - 50)
        )
        inst_rect = inst_surf.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 + 50)
        )

        self.screen.blit(title_surf, title_rect)
        self.screen.blit(inst_surf, inst_rect)

    def draw_end_screen(self, title, title_color, instruction):
        """Função genérica para desenhar telas de fim de jogo."""
        self.draw_gameplay()
        overlay = pygame.Surface(
            (self.screen_width, self.screen_height), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        title_surf = self.title_font.render(title, True, title_color)
        inst_surf = self.instructions_font.render(instruction, True, WHITE)

        title_rect = title_surf.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 - 50)
        )
        inst_rect = inst_surf.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 + 50)
        )

        self.screen.blit(title_surf, title_rect)
        self.screen.blit(inst_surf, inst_rect)

    def run(self):
        """Loop principal do jogo, agora controlado pela máquina de estados."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            if self.game_state == "start_screen":
                self.handle_menu_events()
                self.draw_start_screen()

            elif self.game_state == "playing":
                self.handle_gameplay_events()
                self.update(dt)
                self.draw_gameplay()

            elif self.game_state == "game_over":
                self.handle_menu_events()
                self.draw_end_screen(
                    "GAME OVER", RED, "Pressione R para reiniciar ou ESC para sair"
                )

            elif self.game_state == "win_screen":
                self.handle_menu_events()
                self.draw_end_screen(
                    "VOCÊ VENCEU!", GREEN, "Pressione R para reiniciar ou ESC para sair"
                )

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def draw_minimap(self):
        """Desenha um minimapa no canto superior direito da tela."""
        cell_size = 20
        padding = 4
        border_size = 2
        total_width = (GRID_SIZE * cell_size) + ((GRID_SIZE - 1) * padding)
        total_height = (GRID_SIZE * cell_size) + ((GRID_SIZE - 1) * padding)
        map_x = self.screen_width - total_width - 10
        map_y = 10
        background_rect = pygame.Rect(
            map_x - border_size,
            map_y - border_size,
            total_width + (border_size * 2),
            total_height + (border_size * 2),
        )
        pygame.draw.rect(self.screen, BLACK, background_rect)
        pygame.draw.rect(self.screen, WHITE, background_rect, 1)  # Borda branca
        player_grid_x = int(self.player.x // AREA_WIDTH)
        player_grid_y = int(self.player.y // AREA_HEIGHT)
        player_area_coord = (player_grid_x, player_grid_y)
        for gx in range(GRID_SIZE):
            for gy in range(GRID_SIZE):
                coord = (gx, gy)
                if coord == player_area_coord:
                    color = YELLOW
                elif coord in self.world_grid.active_areas:
                    color = GREEN
                else:
                    color = GRAY
                rect_x = map_x + gx * (cell_size + padding)
                rect_y = map_y + gy * (cell_size + padding)
                pygame.draw.rect(
                    self.screen, color, (rect_x, rect_y, cell_size, cell_size)
                )


if __name__ == "__main__":
    game = Game()
    game.run()
