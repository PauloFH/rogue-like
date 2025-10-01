"""
Utilitário para Gerenciamento de Sprite Sheets

Este arquivo fornece uma classe auxiliar, `SpriteSheet`, para carregar uma única
imagem (spritesheet) e extrair dela frames individuais (sub-imagens).
Isso simplifica o processo de criação de animações a partir de uma folha de sprites.
"""
import pygame


class SpriteSheet:
    """
    Classe para facilitar o trabalho com folhas de sprites (sprite sheets).
    """
    def __init__(self, filename):
        """
        Carrega a folha de sprites do arquivo especificado.

        Args:
            filename (str): O caminho para o arquivo da folha de sprites.
        """
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
