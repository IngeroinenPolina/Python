import curses
import curses.textpad
from life import GameOfLife
from ui import UI
from time import sleep

class Console(UI):
    def __init__(self, life: GameOfLife) -> None:
        super().__init__(life)
        self.speed = speed
    def draw_borders(self, screen) -> None:
        """ Отобразить рамку. """
        curses.textpad.rectangle(self.screen, 0, 0, self.life.rows + 1, self.life.cols + 1)

    def draw_grid(self, screen) -> None:
        """ Отобразить состояние клеток. """
        for i in range(self.life.rows):
            for j in range(self.life.cols):
                if self.life.curr_generation[i][j] == 1:
                    self.screen.addch(i + 1, j + 1, 'O')
                else:
                    self.screen.addch(i + 1, j + 1, '.')

    def run(self) -> None:
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()

        self.draw_borders()

        running = True
        while running:
            self.screen.erase()
            self.draw_borders()
            self.draw_grid()
            self.screen.refresh()

            sleep(1 / self.speed)

            self.life.step()
        curses.endwin()
if __name__ == "__main__":
    game = GameOfLife(size=(10,10))
    console = Console(game)
    console.run()