import curses
from life import GameOfLife
from ui import UI
from time import sleep


class Console(UI):

    def __init__(self, life: GameOfLife) -> None:
        super().__init__(life)
        self.screen = curses.initscr()

    def draw_borders(self) -> None:
        self.screen.border(0)

    def draw_grid(self) -> None:
        """ Отобразить состояние клеток. """
        for i in range(self.life.rows):
            for j in range(self.life.cols):
                if self.life.curr_generation[i][j] == 1:
                    self.screen.addch(i + 1, j + 1, '*')
                else:
                    self.screen.addch(i + 1, j + 1, ' ')

    def run(self) -> None:
        self.draw_borders()

        running = True
        while running:
            self.draw_borders()
            self.draw_grid()
            self.screen.refresh()
            
            sleep(0.5)

            self.life.step()

        curses.endwin()


if __name__ == "__main__":
    game = GameOfLife(size=(10, 10))
    console = Console(game)
    console.run()