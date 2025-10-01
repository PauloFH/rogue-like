import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


class Viewport:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT

    def update(self, target_x, target_y):
        self.x = target_x - self.width // 2
        self.y = target_y - self.height // 2

    def world_to_screen(self, world_x, world_y):
        return world_x - self.x, world_y - self.y

    def is_visible(self, x, y, width=0, height=0):
        return (
            x + width > self.x
            and x < self.x + self.width
            and y + height > self.y
            and y < self.y + self.height
        )
