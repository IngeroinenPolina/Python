import pygame
from life import GameOfLife
from pygame.locals import *
from ui import UI


class GUI(UI):
    def __init__(self, life: GameOfLife, cell_size: int = 10, speed: int = 10) -> None:
        super().__init__(life)
        self.cell_size = cell_size
        self.speed = speed

        self.width = self.cell_size * self.life.cols
        self.height = self.cell_size * self.life.rows

        self.screen_size = self.width, self.height
        self.screen = pygame.display.set_mode(self.screen_size)

    def draw_lines(self) -> None:
        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color('black'),
                             (x, 0), (x, self.height))
            for y in range(0, self.height, self.cell_size):
                pygame.draw.line(self.screen, pygame.Color('black'),
                                 (0, y), (self.width, y))

    def draw_grid(self) -> None:
        for i in range(self.life.rows):
            for j in range(self.life.cols):
                if self.life.curr_generation[i][j] == 1:
                    x = j * self.cell_size
                    y = i * self.cell_size
                pygame.draw.rect(self.screen, pygame.Color('green'), (x+1, y+1, self.cell_size-1, self.cell_size-1))

    def run(self) -> None:
        pygame.init()
        clock = pygame.time.Clock()
        pygame.display.set_caption('Game of Life')
        self.screen.fill(pygame.Color('white'))

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

            self.screen.fill(pygame.Color('white'))
            self.draw_lines()
            self.draw_grid()
            self.life.step()

            pygame.display.flip()
            clock.tick(self.speed)

        pygame.quit()

if __name__ == "__main__":
    game = GameOfLife(size=(50,100))
    gui = GUI(game)
    gui.run()