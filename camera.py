class Viewport:
    def __init__(self, screen_width, screen_height):
        self.x = 0
        self.y = 0
        self.width = screen_width
        self.height = screen_height

    def update(self, target_x, target_y):
        self.x = target_x - self.width // 2
        self.y = target_y - self.height // 2

    def update_size(self, new_width, new_height):
        self.width = new_width
        self.height = new_height

    def world_to_screen(self, world_x, world_y):
        return world_x - self.x, world_y - self.y

    def is_visible(self, x, y, width=0, height=0):
        return (
            x + width > self.x
            and x < self.x + self.width
            and y + height > self.y
            and y < self.y + self.height
        )

