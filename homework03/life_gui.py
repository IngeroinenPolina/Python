import pygame
from pygame.locals import *

import life
from life import GameOfLife
from ui import UI


class GUI(UI):
    def __init__(self, life: GameOfLife, cell_size: int = 10, speed: int = 10) -> None:
        super().__init__(life)
        self.cell_size = cell_size
        self.speed = speed
        self.width = self.life.cols * cell_size
        self.height = self.life.rows * cell_size
        self.screen_size = self.width, self.height
        self.screen = pygame.display.set_mode((self.width, self.height))

    def change_state(self, cell: life.Cell) -> None:
        cell_a = cell[0] // self.cell_size
        cell_b = cell[1] // self.cell_size
        if self.life.curr_generation[cell_a][cell_b]:
            self.life.curr_generation[cell_a][cell_b] = 0
        else:
            self.life.curr_generation[cell_a][cell_b] = 1

    def draw_lines(self) -> None:
        # Copy from previous assignment
        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(
                self.screen, pygame.Color("black"), (x, 0), (x, self.height)
            )
        for y in range(0, self.height, self.cell_size):
            pygame.draw.line(
                self.screen, pygame.Color("black"), (0, y), (self.width, y)
            )

    def draw_grid(self) -> None:
        # Copy from previous assignment
        for i in range(self.life.rows):
            for j in range(self.life.cols):
                if self.life.curr_generation[i][j]:
                    pygame.draw.rect(
                        self.screen,
                        pygame.Color("green"),
                        (
                            j * self.cell_size,
                            i * self.cell_size,
                            self.cell_size,
                            self.cell_size,
                        ),
                    )
                else:
                    pygame.draw.rect(
                        self.screen,
                        pygame.Color("white"),
                        pygame.Rect(
                            j * self.cell_size,
                            i * self.cell_size,
                            self.cell_size,
                            self.cell_size,
                        ),
                    )

    def run(self) -> None:
        # Copy from previous assignment
        pygame.init()
        clock = pygame.time.Clock()
        pygame.display.set_caption("Game of Life")
        self.screen.fill(pygame.Color("white"))
        running = True
        pause = False
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    (cell_y, cell_x) = pygame.mouse.get_pos()
                    self.change_state((cell_x, cell_y))
                    self.draw_grid()
                    self.draw_lines()
                    pygame.display.flip()
                    clock.tick(self.speed)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        pause = not pause
            if not pause:
                self.life.step()

            self.draw_grid()
            self.draw_lines()

            pygame.display.flip()
            clock.tick(self.speed)
        pygame.quit()




if __name__ == "__main__":
    game = GameOfLife(size=(40, 80))
    gui = GUI(game)
    gui.run()