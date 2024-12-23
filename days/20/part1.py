import sys
from itertools import count, product
from pathlib import Path
from typing import NamedTuple

import numpy as np
import pytest
from icecream import ic

# --> Puzzle solution

MOVES = {">": (0, 1), "<": (0, -1), "^": (-1, 0), "v": (1, 0)}
POSSIBLE_TURNS = {
    ">": {
        "^",
        "v",
    },
    "<": {
        "^",
        "v",
    },
    "^": {
        ">",
        "<",
    },
    "v": {
        ">",
        "<",
    },
}


def go(pos, direction):
    move = MOVES[direction]
    return pos[0] + move[0], pos[1] + move[1]


class Cursor(NamedTuple):
    pos: tuple[int, int]
    direction: str


class Cheat(NamedTuple):
    start_pos: tuple[int, int]
    end_pos: tuple[int, int]


class Maze:
    def __init__(self, grid):
        self.path = np.zeros_like(grid, dtype=int)
        max_i, max_j = grid.shape
        start = np.where(grid == "S")
        self.start_pos = start[0][0], start[1][0]
        end = np.where(grid == "E")
        self.end_pos = end[0][0], end[1][0]

        grid[self.start_pos] = "."
        grid[self.end_pos] = "."

        self.walls = {
            (i, j) for i, j in product(range(max_i), range(max_j)) if grid[i, j] == "#"
        }
        self.fill_initial_path()

        self.cheat_points = self.find_cheat_points(grid)
        self.clean_up_cheat_list()

    def wall(self, pos):
        return pos in self.walls

    def fill_initial_path(self):
        timestep = count(1)

        # Find a legal direction for the first step
        for move in MOVES:
            if not self.wall(go(self.start_pos, move)):
                cursor = Cursor(self.start_pos, move)
                break
        else:
            raise Exception("oops")

        self.path[cursor.pos] = next(timestep)

        while cursor.pos != self.end_pos:
            proposed = go(cursor.pos, cursor.direction)
            if not self.wall(proposed):
                cursor = Cursor(proposed, cursor.direction)
                self.path[cursor.pos] = next(timestep)
            else:
                for move in POSSIBLE_TURNS[cursor.direction]:
                    proposed = go(cursor.pos, move)
                    if not self.wall(proposed):
                        cursor = Cursor(proposed, move)
                        self.path[cursor.pos] = next(timestep)
                        break
                else:
                    raise Exception("oops")

    def clean_up_cheat_list(self):
        new_cheats = []
        for cheat in self.cheat_points:
            if (self.path[cheat.start_pos] != 0) and (self.path[cheat.end_pos] != 0):
                new_cheats.append(cheat)
        self.cheat_points = new_cheats

    def find_cheat_points(self, grid):
        max_i, max_j = grid.shape

        cheat_points = []
        for i, j in product(range(max_i), range(max_j)):
            cheat_start = (i, j)

            # check for horizontal cheats
            if is_cheat(grid[i, j : j + 3]):
                cheat_points.append(Cheat(cheat_start, (i, j + 2)))

            # check for vertical cheats
            if is_cheat(grid[i : i + 3, j]):
                cheat_points.append(Cheat(cheat_start, (i + 2, j)))

        return cheat_points

    def evaluate_cheat(self, cheat):
        savings = abs(self.path[cheat.end_pos] - self.path[cheat.start_pos]) - 2
        if savings > 0:
            return savings
        return 0

    def score(self, threshold):
        return sum(
            (self.evaluate_cheat(cheat) >= threshold) for cheat in self.cheat_points
        )

    def count(self, threshold):
        return sum(
            (self.evaluate_cheat(cheat) == threshold) for cheat in self.cheat_points
        )


def read_input(input_data):
    return np.array([list(row) for row in input_data.splitlines()], dtype="str")


def is_cheat(a1):
    a1 = a1.flatten()
    pat = np.array([".", "#", "."])
    return (a1.shape == pat.shape) and np.all(a1 == pat)


def solve(input_data, threshold):
    grid = read_input(input_data)
    puzzle = Maze(grid)
    return puzzle.score(threshold)


# --> Test driven development helpers


# Test any examples given in the problem

sample_input = Path("input-sample.txt").read_text().strip()
EXAMPLES = [
    (sample_input, 2, 14),
    (sample_input, 4, 14),
    (sample_input, 6, 2),
    (sample_input, 8, 4),
    (sample_input, 10, 2),
    (sample_input, 12, 3),
    (sample_input, 20, 1),
    (sample_input, 36, 1),
    (sample_input, 38, 1),
    (sample_input, 40, 1),
    (sample_input, 64, 1),
]


@pytest.mark.parametrize("sample_data,threshold,sample_solution", EXAMPLES)
def test_samples(sample_data, threshold, sample_solution) -> None:
    grid = read_input(sample_data)
    puzzle = Maze(grid)
    assert puzzle.count(threshold) == sample_solution


# --> Setup and run

if __name__ == "__main__":
    #  Run the test examples with icecream debug-trace turned on
    ic.enable()
    ex = pytest.main([__file__, "--capture=tee-sys", "-v"])
    if ex not in {pytest.ExitCode.OK, pytest.ExitCode.NO_TESTS_COLLECTED}:
        print(f"tests FAILED ({ex})")
        sys.exit(1)
    else:
        print("tests PASSED")

    #  Actual input data generally has more iterations, turn off log
    ic.disable()
    my_input = Path("input.txt").read_text().strip()
    result = solve(my_input, 100)
    print(result)
