# sprites.py
import pygame


class SpriteSheet:
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert_alpha()
        except pygame.error as e:
            print(f"Não foi possível carregar a spritesheet: {filename}")
            raise SystemExit(e)

    def get_image(self, x, y, width, height):
        """Pega um único frame da spritesheet."""
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        return image
