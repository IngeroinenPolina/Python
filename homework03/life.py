import pathlib
import random
# import pygame
import json

from typing import List, Optional, Tuple


Cell = Tuple[int, int]
Cells = List[int]
Grid = List[Cells]


class GameOfLife:
    def __init__(
        self,
        size: Tuple[int, int],
        randomize: bool = True,
        max_generations: Optional[float] = float("inf"),
    ) -> None:
        # Размер клеточного поля
        self.rows, self.cols = size
        # Предыдущее поколение клеток
        self.prev_generation = self.create_grid()
        # Текущее поколение клеток
        self.curr_generation = self.create_grid(randomize=randomize)
        # Максимальное число поколений
        self.max_generations = max_generations
        # Текущее число поколений
        self.generations = 1

    def create_grid(self, randomize: bool = False) -> Grid:
        grid = []
        for i in range(self.rows):
            line = []

            for j in range(self.cols):
                if randomize:
                    box = random.randint(0, 1)
                else:
                    box = 0

                line.append(box)
            grid.append(line)

        return grid

    def get_neighbours(self, cell: Cell) -> Cells:
        list_all_neighbours = []
        for i in range(cell[0] - 1, cell[0] + 2):
            if i >= self.rows or i < 0:
                continue
            for j in range(cell[1] - 1, cell[1] + 2):
                if j >= self.cols or j < 0:
                    continue
                if i == cell[0] and j == cell[1]:
                    continue
                list_all_neighbours.append(self.curr_generation[i][j])
        return list_all_neighbours

    def get_next_generation(self) -> Grid:
        next_grid = self.create_grid(False)
        for i in range(self.rows):
            for j in range(self.cols):
                if self.curr_generation[i][j] == 1:
                    if 2 <= sum(self.get_neighbours((i,j))) <= 3:
                        next_grid[i][j] = 1
                    else:
                        next_grid[i][j] = 0
                else:
                    if sum(self.get_neighbours((i,j))) == 3:
                        next_grid[i][j] = 1
                    else:
                        next_grid[i][j] = 0

        return next_grid

    def step(self) -> None:
        self.prev_generation = self.curr_generation
        self.curr_generation = self.get_next_generation()
        self.generations += 1

    @property
    def is_max_generations_exceeded(self) -> bool:
        return self.generations >= self.max_generations

    @property
    def is_changing(self) -> bool:
        rows = len(self.prev_generation)
        for i in range(rows):
            cols = len(self.prev_generation[i])
            for j in range (cols):
                if self.curr_generation[i][j] != self.prev_generation[i][j]:
                    return True
        return False

    @staticmethod
    def from_file(filename: pathlib.Path) -> "GameOfLife":
        with open(filename, 'r') as file:
            ob = json.load(file)

        game = GameOfLife(
            size=(ob['rows'], ob['cols']),
            randomize=False,
            max_generations=ob['max_generations']
        )

        game.prev_generation = ob['prev_generation']
        game.curr_generation = ob['curr_generation']
        game.generations = ob['generations']
        return game

    def save(self, filename: pathlib.Path) -> None:
        json_obj = {
            'rows': self.rows,
            'cols': self.cols,
            'prev_generation': self.prev_generation,
            'curr_generation': self.curr_generation,
            'max_generations': self.max_generations,
            'generations': self.generations
        }
        with open(filename, 'w') as file:
            json.dump(json_obj, file)