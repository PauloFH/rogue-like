"""
Implementação da Câmera (Viewport)

Este arquivo define a classe Viewport, que funciona como uma câmera, controlando
qual parte do mundo do jogo é visível na tela.

REQUISITO ATENDIDO:
- "A janela de visualização (viewport) deve ser independente da malha":
  A classe Viewport gerencia uma visão (câmera) que se move pelo mundo do jogo
  independentemente da estrutura de áreas. Ela converte as coordenadas do mundo
  para coordenadas de tela, permitindo que o jogador veja apenas uma porção
  do mapa de cada vez. O zoom e o redimensionamento da janela são gerenciados
  de forma que a visão do jogo se adapte, mantendo a independência.
"""
import pygame



class Viewport:
    """
    Controla a porção visível do mundo do jogo.

    Funciona como uma câmera que segue o jogador, determinando quais
    coordenadas do mundo devem ser desenhadas na tela.
    """
    def __init__(self, screen_width, screen_height):
        """
        Inicializa a viewport com as dimensões da superfície de jogo.

        Args:
            screen_width (int): Largura da superfície onde o jogo é desenhado.
            screen_height (int): Altura da superfície onde o jogo é desenhado.
        """
        self.x = 0
        self.y = 0
        self.width = screen_width
        self.height = screen_height

    def update(self, target_x, target_y):
        """
        Atualiza a posição da câmera para centralizar em um alvo (o jogador).

        Args:
            target_x (float): Coordenada X do alvo no mundo.
            target_y (float): Coordenada Y do alvo no mundo.
        """
        self.x = target_x - self.width // 2
        self.y = target_y - self.height // 2

    def update_size(self, new_width, new_height):
        """
        Atualiza as dimensões da viewport, útil ao redimensionar a janela.
        """
        self.width = new_width
        self.height = new_height

    def world_to_screen(self, world_x, world_y):
        """
        Converte coordenadas do mundo para coordenadas relativas à tela.

        Returns:
            tuple[int, int]: A posição (x, y) para desenhar na superfície.
        """
        return world_x - self.x, world_y - self.y

    def is_visible(self, x, y, width=0, height=0):
        """
        Verifica se um retângulo (dado por x, y, width, height) está visível
        dentro da área da câmera. Usado para otimizar o desenho (culling).
        """
        return (
            x + width > self.x
            and x < self.x + self.width
            and y + height > self.y
            and y < self.y + self.height
        )
